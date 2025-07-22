"""
Fixed Django Database Backend for Azure SQL with Entra Authentication
This removes the Integrated Security conflict that django-mssql incorrectly adds
"""

from mssql import base


class DatabaseWrapper(base.DatabaseWrapper):
    """
    Django database wrapper for Azure SQL that properly handles Entra authentication
    """
    
    def get_connection_params(self):
        """Override to remove Integrated Security that conflicts with Entra auth"""
        settings_dict = self.settings_dict
        
        # Start with the standard connection parameters
        conn_params = {
            'server': settings_dict['HOST'],
            'port': settings_dict.get('PORT', 1433),
            'database': settings_dict['NAME'],
            'user': settings_dict.get('USER', ''),
            'password': settings_dict.get('PASSWORD', ''),
        }
        
        # Add driver and options
        options = settings_dict.get('OPTIONS', {})
        if 'driver' in options:
            conn_params['driver'] = options['driver']
        else:
            conn_params['driver'] = 'ODBC Driver 17 for SQL Server'
            
        # Add extra parameters (this includes our Entra auth)
        if 'extra_params' in options:
            conn_params['extra_params'] = options['extra_params']
            
        return conn_params
    
    def _get_new_connection(self, conn_params):
        """Create connection without Integrated Security"""
        import pyodbc
        
        # Build connection string manually to avoid django-mssql adding Integrated Security
        conn_parts = [
            f"DRIVER={{{conn_params['driver']}}}",
            f"SERVER={conn_params['server']},{conn_params['port']}",
            f"DATABASE={conn_params['database']}",
        ]
        
        # Add extra parameters (our Entra auth settings)
        if 'extra_params' in conn_params:
            conn_parts.append(conn_params['extra_params'])
        
        conn_string = ';'.join(conn_parts)
        
        try:
            connection = pyodbc.connect(conn_string)
            return connection
        except Exception as e:
            from django.db import DatabaseError
            raise DatabaseError(f"Error connecting to Azure SQL: {e}")
