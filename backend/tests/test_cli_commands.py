"""
Tests for CLI user management commands.

This module tests the CLI functionality including user creation, password reset,
enable/disable operations, and user deletion.
"""

import pytest
import tempfile
import os
from unittest.mock import patch
from click.testing import CliRunner
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, DateTime, ForeignKey, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

from app.cli.user_commands import user
from app.models.user import DEFAULT_TENANT_ID


class TestUserCommandsIsolated:
    """Test suite for user CLI commands with isolated database per test."""
    
    def create_test_db(self):
        """Create a fresh test database for each test."""
        # Create temporary file
        tmp_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        db_path = tmp_file.name
        tmp_file.close()
        
        # Create engine for temporary database
        engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
        
        # Create basic tables
        metadata = MetaData()
        
        # Tenants table
        tenants_table = Table(
            'tenants', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String, nullable=False),
            Column('slug', String, nullable=False, unique=True),
            Column('is_active', Boolean, nullable=False, default=True),
            Column('created_at', DateTime(timezone=True), server_default=func.now(), nullable=False)
        )
        
        # Users table
        users_table = Table(
            'users', metadata,
            Column('id', Integer, primary_key=True),
            Column('email', String, unique=True, nullable=False),
            Column('hashed_password', String, nullable=False),
            Column('full_name', String),
            Column('is_active', Boolean, default=True),
            Column('is_superuser', Boolean, default=False),
            Column('created_at', DateTime(timezone=True), server_default=func.now()),
            Column('updated_at', DateTime(timezone=True), onupdate=func.now()),
            Column('tenant_id', Integer, ForeignKey('tenants.id'), nullable=False, default=DEFAULT_TENANT_ID)
        )
        
        # Create all tables
        metadata.create_all(engine)
        
        # Create default tenant
        Session = sessionmaker(bind=engine)
        db = Session()
        try:
            from datetime import datetime
            db.execute(text("""
                INSERT INTO tenants (id, name, slug, is_active, created_at) 
                VALUES (:id, :name, :slug, :is_active, :created_at)
            """), {
                "id": DEFAULT_TENANT_ID,
                "name": "Test Tenant",
                "slug": "test",
                "is_active": True,
                "created_at": datetime.utcnow().replace(tzinfo=None)
            })
            db.commit()
        finally:
            db.close()
        
        return db_path, Session
    
    def run_with_test_db(self, command_args):
        """Run a CLI command with a fresh test database."""
        db_path, Session = self.create_test_db()
        
        try:
            # Patch the database session
            with patch('app.cli.user_commands.get_db_session', return_value=Session()):
                runner = CliRunner()
                result = runner.invoke(user, command_args)
                return result
        finally:
            # Cleanup
            try:
                os.unlink(db_path)
            except OSError:
                pass
    
    def test_create_user_success(self):
        """Test successful user creation."""
        result = self.run_with_test_db([
            'create-user',
            '--email', 'test@example.com',
            '--password', 'testpassword123',
            '--full-name', 'Test User',
            '--tenant-id', str(DEFAULT_TENANT_ID)
        ])
        
        assert result.exit_code == 0
        assert "✅ User created successfully:" in result.output
        assert "test@example.com" in result.output
        assert "Test User" in result.output
    
    def test_create_user_duplicate_email(self):
        """Test creating user with duplicate email."""
        db_path, Session = self.create_test_db()
        
        try:
            # Patch the database session for both commands
            with patch('app.cli.user_commands.get_db_session', return_value=Session()):
                runner = CliRunner()
                
                # Create first user
                result1 = runner.invoke(user, [
                    'create-user',
                    '--email', 'test@example.com',
                    '--password', 'testpassword123',
                    '--full-name', 'Test User',
                    '--tenant-id', str(DEFAULT_TENANT_ID)
                ])
                assert result1.exit_code == 0
                
                # Try to create duplicate
                result2 = runner.invoke(user, [
                    'create-user',
                    '--email', 'test@example.com',
                    '--password', 'testpassword456',
                    '--full-name', 'Test User 2',
                    '--tenant-id', str(DEFAULT_TENANT_ID)
                ])
                
                assert result2.exit_code == 0
                assert "❌ Error: User with email 'test@example.com' already exists" in result2.output
        finally:
            try:
                os.unlink(db_path)
            except OSError:
                pass
    
    def test_create_superuser_success(self):
        """Test successful superuser creation."""
        result = self.run_with_test_db([
            'create-superuser',
            '--email', 'admin@example.com',
            '--password', 'adminpassword123',
            '--full-name', 'Admin User',
            '--tenant-id', str(DEFAULT_TENANT_ID)
        ])
        
        assert result.exit_code == 0
        assert "✅ Superuser created successfully:" in result.output
        assert "admin@example.com" in result.output
        assert "Superuser: True" in result.output
    
    def test_list_users_empty(self):
        """Test listing users when none exist."""
        result = self.run_with_test_db(['list-users'])
        
        assert result.exit_code == 0
        assert "ℹ️  No users found" in result.output
    
    def test_reset_password_user_not_found(self):
        """Test resetting password for non-existent user."""
        result = self.run_with_test_db([
            'reset-password',
            '--email', 'nonexistent@example.com',
            '--tenant-id', str(DEFAULT_TENANT_ID),
            '--new-password', 'newpassword456'
        ])
        
        assert result.exit_code == 0
        assert "❌ Error: User with email 'nonexistent@example.com' not found" in result.output
    
    def test_enable_disable_operations(self):
        """Test enable/disable operations."""
        db_path, Session = self.create_test_db()
        
        try:
            with patch('app.cli.user_commands.get_db_session', return_value=Session()):
                runner = CliRunner()
                
                # Create a user
                result1 = runner.invoke(user, [
                    'create-user',
                    '--email', 'test@example.com',
                    '--password', 'testpassword123',
                    '--full-name', 'Test User',
                    '--tenant-id', str(DEFAULT_TENANT_ID)
                ])
                assert result1.exit_code == 0
                
                # Disable the user
                result2 = runner.invoke(user, [
                    'disable-user',
                    '--email', 'test@example.com',
                    '--tenant-id', str(DEFAULT_TENANT_ID)
                ])
                assert result2.exit_code == 0
                assert "✅ User disabled successfully:" in result2.output
                
                # Enable the user
                result3 = runner.invoke(user, [
                    'enable-user',
                    '--email', 'test@example.com',
                    '--tenant-id', str(DEFAULT_TENANT_ID)
                ])
                assert result3.exit_code == 0
                assert "✅ User enabled successfully:" in result3.output
        finally:
            try:
                os.unlink(db_path)
            except OSError:
                pass
    
    def test_password_reset_workflow(self):
        """Test complete password reset workflow."""
        db_path, Session = self.create_test_db()
        
        try:
            with patch('app.cli.user_commands.get_db_session', return_value=Session()):
                runner = CliRunner()
                
                # Create a user
                result1 = runner.invoke(user, [
                    'create-user',
                    '--email', 'test@example.com',
                    '--password', 'testpassword123',
                    '--full-name', 'Test User',
                    '--tenant-id', str(DEFAULT_TENANT_ID)
                ])
                assert result1.exit_code == 0
                
                # Reset password
                result2 = runner.invoke(user, [
                    'reset-password',
                    '--email', 'test@example.com',
                    '--tenant-id', str(DEFAULT_TENANT_ID),
                    '--new-password', 'newpassword456'
                ])
                assert result2.exit_code == 0
                assert "✅ Password reset successfully for user:" in result2.output
        finally:
            try:
                os.unlink(db_path)
            except OSError:
                pass