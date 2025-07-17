"""
Custom Django Database Backend for Azure SQL with Azure AD
This backend fixes the "Integrated Security" conflict issue
"""

from mssql.base import DatabaseWrapper as MSSQLDatabaseWrapper
from mssql.base import DatabaseOperations as MSSQLDatabaseOperations
from django.db.backends.base.base import BaseDatabaseWrapper


class DatabaseOperations(MSSQLDatabaseOperations):
    pass


class DatabaseWrapper(MSSQLDatabaseWrapper):
    """
    Custom Azure SQL database wrapper that properly handles Azure AD authentication
    """
    
    def get_connection_params(self):
        """Override to fix Azure AD authentication conflicts"""
        settings_dict = self.settings_dict
        
        # Get the connection parameters from parent
        conn_params = super().get_connection_params()
        
        # Remove any conflicting parameters
        if 'trusted_connection' in conn_params:
            del conn_params['trusted_connection']
        if 'Trusted_Connection' in conn_params:
            del conn_params['Trusted_Connection']
            
        return conn_params
    
    def _get_new_connection(self, conn_params):
        """Override connection creation to avoid Integrated Security conflicts"""
        settings_dict = self.settings_dict
        
        # Build connection string manually for Azure AD
        conn_string_parts = []
        
        # Required parameters
        conn_string_parts.append(f"DRIVER={{{conn_params.get('driver', 'ODBC Driver 17 for SQL Server')}}}")
        conn_string_parts.append(f"SERVER={settings_dict['HOST']},{settings_dict['PORT']}")
        conn_string_parts.append(f"DATABASE={settings_dict['NAME']}")
        
        # Add extra parameters (including Azure AD authentication)
        if 'extra_params' in settings_dict.get('OPTIONS', {}):
            extra_params = settings_dict['OPTIONS']['extra_params']
            if isinstance(extra_params, str):
                # Split extra_params and add each one
                for param in extra_params.split(';'):
                    if param.strip():
                        conn_string_parts.append(param.strip())
        
        # Build final connection string
        conn_string = ';'.join(conn_string_parts)
        
        # Import pyodbc and connect
        import pyodbc
        return pyodbc.connect(conn_string)
    
    def get_new_connection(self, conn_params):
        """Use our custom connection method"""
        return self._get_new_connection(conn_params)
