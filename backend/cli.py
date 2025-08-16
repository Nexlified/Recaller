#!/usr/bin/env python3
"""
Recaller Backend CLI Tool

This script provides command-line interface for managing Recaller backend operations.
It includes user management, tenant operations, and other administrative tasks.

Usage:
    python cli.py --help
    python cli.py user --help
    python cli.py user create-user
    python cli.py user list-users
"""

import click
import sys
import os
from typing import Optional

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.cli.user_commands import user
from app.db.session import SessionLocal
from app.models.tenant import Tenant


@click.group()
@click.version_option(version="1.0.0", prog_name="Recaller CLI")
def cli():
    """
    🚀 Recaller Backend CLI Tool
    
    Administrative command-line interface for managing Recaller backend.
    """
    pass


@cli.group()
def tenant():
    """Tenant management commands."""
    pass


@tenant.command()
@click.option('--limit', default=20, help='Maximum number of tenants to display')
def list_tenants(limit: int):
    """List all tenants."""
    db = SessionLocal()
    try:
        tenants = db.query(Tenant).limit(limit).all()
        
        if not tenants:
            click.echo("ℹ️  No tenants found")
            return
        
        click.echo(f"📋 Found {len(tenants)} tenant(s):")
        click.echo("-" * 60)
        
        for tenant in tenants:
            status = "🟢 Active" if tenant.is_active else "🔴 Inactive"
            click.echo(f"ID: {tenant.id:4} | {status} | {tenant.slug:20} | {tenant.name}")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")
    finally:
        db.close()


@tenant.command()
@click.option('--name', prompt=True, help='Tenant display name')
@click.option('--slug', prompt=True, help='Tenant slug (unique identifier)')
@click.option('--is-active/--is-inactive', default=True, help='Tenant active status')
def create_tenant(name: str, slug: str, is_active: bool):
    """Create a new tenant."""
    db = SessionLocal()
    try:
        # Check if tenant slug already exists
        existing_tenant = db.query(Tenant).filter(Tenant.slug == slug).first()
        if existing_tenant:
            click.echo(f"❌ Error: Tenant with slug '{slug}' already exists")
            return
        
        # Create tenant
        tenant = Tenant(
            name=name,
            slug=slug,
            is_active=is_active
        )
        
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        
        click.echo(f"✅ Tenant created successfully:")
        click.echo(f"   ID: {tenant.id}")
        click.echo(f"   Name: {tenant.name}")
        click.echo(f"   Slug: {tenant.slug}")
        click.echo(f"   Active: {tenant.is_active}")
        
    except Exception as e:
        db.rollback()
        click.echo(f"❌ Error: {str(e)}")
    finally:
        db.close()


@cli.command()
def health():
    """Check database connection and system health."""
    try:
        from sqlalchemy import text
        db = SessionLocal()
        # Test database connection
        db.execute(text("SELECT 1"))
        db.close()
        
        click.echo("✅ Database connection: OK")
        click.echo("✅ System health: OK")
        
    except Exception as e:
        click.echo(f"❌ Database connection: FAILED - {str(e)}")
        click.echo("❌ System health: FAILED")
        sys.exit(1)


# Register command groups
cli.add_command(user)
cli.add_command(tenant)


if __name__ == '__main__':
    cli()