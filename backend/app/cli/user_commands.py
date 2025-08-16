"""
User management CLI commands for Recaller backend.

This module provides CLI commands for managing users including:
- Creating users
- Resetting passwords
- Enabling/disabling accounts
- Deleting users and their data
"""

import click
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.session import SessionLocal
from app.crud import user as crud_user
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from app.models.user import DEFAULT_TENANT_ID


def get_db_session() -> Session:
    """Get database session for CLI operations."""
    return SessionLocal()


@click.group()
def user():
    """User management commands."""
    pass


@user.command()
@click.option('--email', prompt=True, help='User email address')
@click.option('--password', prompt=True, hide_input=True, help='User password')
@click.option('--full-name', prompt=True, help='User full name')
@click.option('--tenant-id', default=DEFAULT_TENANT_ID, help=f'Tenant ID (default: {DEFAULT_TENANT_ID})')
@click.option('--is-superuser', is_flag=True, help='Create as superuser')
@click.option('--is-active/--is-inactive', default=True, help='User active status')
def create_user(email: str, password: str, full_name: str, tenant_id: int, is_superuser: bool, is_active: bool):
    """Create a new user."""
    db = get_db_session()
    try:
        # Check if user already exists
        existing_user = crud_user.get_user_by_email(db=db, email=email, tenant_id=tenant_id)
        if existing_user:
            click.echo(f"❌ Error: User with email '{email}' already exists in tenant {tenant_id}")
            return
        
        # Create user
        user_data = UserCreate(
            email=email,
            password=password,
            full_name=full_name,
            is_active=is_active
        )
        
        user = crud_user.create_user(db=db, obj_in=user_data, tenant_id=tenant_id)
        
        # Set superuser status if requested
        if is_superuser:
            crud_user.update_user(db=db, db_obj=user, obj_in={"is_superuser": True})
            
        click.echo(f"✅ User created successfully:")
        click.echo(f"   ID: {user.id}")
        click.echo(f"   Email: {user.email}")
        click.echo(f"   Full Name: {user.full_name}")
        click.echo(f"   Tenant ID: {user.tenant_id}")
        click.echo(f"   Active: {user.is_active}")
        click.echo(f"   Superuser: {user.is_superuser}")
        
    except IntegrityError as e:
        db.rollback()
        click.echo(f"❌ Error: Failed to create user - {str(e)}")
    except Exception as e:
        db.rollback()
        click.echo(f"❌ Error: {str(e)}")
    finally:
        db.close()


@user.command()
@click.option('--email', prompt=True, help='User email address')
@click.option('--tenant-id', default=DEFAULT_TENANT_ID, help=f'Tenant ID (default: {DEFAULT_TENANT_ID})')
@click.option('--new-password', prompt=True, hide_input=True, help='New password')
def reset_password(email: str, tenant_id: int, new_password: str):
    """Reset user password."""
    db = get_db_session()
    try:
        # Find user
        user = crud_user.get_user_by_email(db=db, email=email, tenant_id=tenant_id)
        if not user:
            click.echo(f"❌ Error: User with email '{email}' not found in tenant {tenant_id}")
            return
        
        # Update password
        updated_user = crud_user.update_user(
            db=db, 
            db_obj=user, 
            obj_in={"password": new_password}
        )
        
        click.echo(f"✅ Password reset successfully for user:")
        click.echo(f"   ID: {updated_user.id}")
        click.echo(f"   Email: {updated_user.email}")
        click.echo(f"   Full Name: {updated_user.full_name}")
        
    except Exception as e:
        db.rollback()
        click.echo(f"❌ Error: {str(e)}")
    finally:
        db.close()


@user.command()
@click.option('--email', prompt=True, help='User email address')
@click.option('--tenant-id', default=DEFAULT_TENANT_ID, help=f'Tenant ID (default: {DEFAULT_TENANT_ID})')
def enable_user(email: str, tenant_id: int):
    """Enable user account."""
    db = get_db_session()
    try:
        # Find user
        user = crud_user.get_user_by_email(db=db, email=email, tenant_id=tenant_id)
        if not user:
            click.echo(f"❌ Error: User with email '{email}' not found in tenant {tenant_id}")
            return
        
        if user.is_active:
            click.echo(f"ℹ️  User '{email}' is already enabled")
            return
        
        # Enable user
        updated_user = crud_user.update_user(
            db=db, 
            db_obj=user, 
            obj_in={"is_active": True}
        )
        
        click.echo(f"✅ User enabled successfully:")
        click.echo(f"   ID: {updated_user.id}")
        click.echo(f"   Email: {updated_user.email}")
        click.echo(f"   Active: {updated_user.is_active}")
        
    except Exception as e:
        db.rollback()
        click.echo(f"❌ Error: {str(e)}")
    finally:
        db.close()


@user.command()
@click.option('--email', prompt=True, help='User email address')
@click.option('--tenant-id', default=DEFAULT_TENANT_ID, help=f'Tenant ID (default: {DEFAULT_TENANT_ID})')
def disable_user(email: str, tenant_id: int):
    """Disable user account."""
    db = get_db_session()
    try:
        # Find user
        user = crud_user.get_user_by_email(db=db, email=email, tenant_id=tenant_id)
        if not user:
            click.echo(f"❌ Error: User with email '{email}' not found in tenant {tenant_id}")
            return
        
        if not user.is_active:
            click.echo(f"ℹ️  User '{email}' is already disabled")
            return
        
        # Disable user
        updated_user = crud_user.update_user(
            db=db, 
            db_obj=user, 
            obj_in={"is_active": False}
        )
        
        click.echo(f"✅ User disabled successfully:")
        click.echo(f"   ID: {updated_user.id}")
        click.echo(f"   Email: {updated_user.email}")
        click.echo(f"   Active: {updated_user.is_active}")
        
    except Exception as e:
        db.rollback()
        click.echo(f"❌ Error: {str(e)}")
    finally:
        db.close()


@user.command()
@click.option('--email', prompt=True, help='User email address')
@click.option('--tenant-id', default=DEFAULT_TENANT_ID, help=f'Tenant ID (default: {DEFAULT_TENANT_ID})')
@click.option('--force', is_flag=True, help='Force deletion without confirmation')
def delete_user(email: str, tenant_id: int, force: bool):
    """Delete user and all associated data."""
    db = get_db_session()
    try:
        # Find user
        user = crud_user.get_user_by_email(db=db, email=email, tenant_id=tenant_id)
        if not user:
            click.echo(f"❌ Error: User with email '{email}' not found in tenant {tenant_id}")
            return
        
        # Confirmation prompt
        if not force:
            click.echo(f"⚠️  Warning: This will permanently delete user and all associated data:")
            click.echo(f"   ID: {user.id}")
            click.echo(f"   Email: {user.email}")
            click.echo(f"   Full Name: {user.full_name}")
            click.echo(f"   Tenant ID: {user.tenant_id}")
            
            if not click.confirm("Are you sure you want to delete this user?"):
                click.echo("❌ Deletion cancelled")
                return
        
        # Delete user
        deleted_user = crud_user.delete_user(db=db, user_id=user.id)
        
        if deleted_user:
            click.echo(f"✅ User deleted successfully:")
            click.echo(f"   ID: {deleted_user.id}")
            click.echo(f"   Email: {deleted_user.email}")
        else:
            click.echo(f"❌ Error: Failed to delete user")
        
    except Exception as e:
        db.rollback()
        click.echo(f"❌ Error: {str(e)}")
    finally:
        db.close()


@user.command()
@click.option('--tenant-id', default=None, help='Filter by tenant ID (default: all tenants)')
@click.option('--active-only', is_flag=True, help='Show only active users')
@click.option('--limit', default=50, help='Maximum number of users to display')
def list_users(tenant_id: Optional[int], active_only: bool, limit: int):
    """List users."""
    from app.models.user import User
    db = get_db_session()
    try:
        if tenant_id is not None:
            # Get users for specific tenant
            users = crud_user.get_users(db=db, tenant_id=tenant_id, limit=limit)
            if active_only:
                users = [u for u in users if u.is_active]
        else:
            # Get all users across tenants
            if active_only:
                users = crud_user.get_all_active(db=db, limit=limit)
            else:
                # Get all users (need to implement this if needed)
                users = db.query(User).limit(limit).all()
        
        if not users:
            click.echo("ℹ️  No users found")
            return
        
        click.echo(f"📋 Found {len(users)} user(s):")
        click.echo("-" * 80)
        
        for user in users:
            status = "🟢 Active" if user.is_active else "🔴 Inactive"
            superuser = " (Superuser)" if user.is_superuser else ""
            click.echo(f"ID: {user.id:4} | {status} | Tenant: {user.tenant_id} | {user.email:30} | {user.full_name or 'N/A'}{superuser}")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")
    finally:
        db.close()


@user.command()
@click.option('--email', prompt=True, help='Superuser email address')
@click.option('--password', prompt=True, hide_input=True, help='Superuser password')
@click.option('--full-name', prompt=True, help='Superuser full name')
@click.option('--tenant-id', default=DEFAULT_TENANT_ID, help=f'Tenant ID (default: {DEFAULT_TENANT_ID})')
def create_superuser(email: str, password: str, full_name: str, tenant_id: int):
    """Create a superuser account."""
    db = get_db_session()
    try:
        # Check if user already exists
        existing_user = crud_user.get_user_by_email(db=db, email=email, tenant_id=tenant_id)
        if existing_user:
            click.echo(f"❌ Error: User with email '{email}' already exists in tenant {tenant_id}")
            return
        
        # Create superuser
        user_data = UserCreate(
            email=email,
            password=password,
            full_name=full_name,
            is_active=True
        )
        
        user = crud_user.create_user(db=db, obj_in=user_data, tenant_id=tenant_id)
        
        # Set superuser status
        superuser = crud_user.update_user(db=db, db_obj=user, obj_in={"is_superuser": True})
        
        click.echo(f"✅ Superuser created successfully:")
        click.echo(f"   ID: {superuser.id}")
        click.echo(f"   Email: {superuser.email}")
        click.echo(f"   Full Name: {superuser.full_name}")
        click.echo(f"   Tenant ID: {superuser.tenant_id}")
        click.echo(f"   Active: {superuser.is_active}")
        click.echo(f"   Superuser: {superuser.is_superuser}")
        
    except IntegrityError as e:
        db.rollback()
        click.echo(f"❌ Error: Failed to create superuser - {str(e)}")
    except Exception as e:
        db.rollback()
        click.echo(f"❌ Error: {str(e)}")
    finally:
        db.close()