# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
{
    "name": "Data Offload / External Archive Manager",
    "version": "18.0.0.0",
    "category": "Tools",
    'author': 'Techultra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    "summary": '''Offload selected model fields to an external PostgreSQL database with retrieve/delete, smart button, and scheduled offload/purge.
    
    tus
    techultra
    techultra_private_limited_solution
    Data Offload 
    External Archive Manager
    Data Offload / External Archive Manager
    PostgreSQL 
    offloading,
    data archiving
    database optimization
    external storage solution
    data retrieval 
    scheduled purge 
    batch processing
    large dataset management
    PostgreSQL data offloading
    External database integration
    Data archiving solution
    Database offload for performance
    Large data management system
    External PostgreSQL storage solution
    Data lifecycle management
    Historical data archiving
    Scheduled data purge system
    Cron job data offloading
    Data retrieval from external databases
    Data retention management solution
    Database size reduction tool
    Offload database fields to external storage
    External database offload solution
    Offload large database fields to PostgreSQL
    Archive inactive data in external PostgreSQL
    Store historical records in external databases
    Retrieve archived data from external storage
    Automate data offloading and purging
    PostgreSQL archive storage for databases
    Data management for high-volume databases
    Performance optimization for databases
    Odoo PostgreSQL data offloading
    Odoo external database integration
    Database Restore
    Odoo data archiving module
    Odoo database offload solution
    Odoo performance optimization module
    Odoo large data management
    Odoo external PostgreSQL storage
    Odoo historical data archiving
    Odoo scheduled data purge
    Odoo cron-based data offload
    Odoo smart button data retrieval
    Odoo data retention management
    Odoo database size reduction
    Odoo offload selected fields
    Odoo external storage solution
    Offload Odoo model fields to PostgreSQL
    Archive old Odoo records in external database
    Reduce Odoo database size with PostgreSQL
    Store Odoo historical data externally
    Retrieve archived Odoo data on demand
    Automate Odoo data offloading and purge
    PostgreSQL archive database for Odoo
    PostgreSQL external data store
    Data lifecycle management for Odoo
    Odoo database scalability solution
    Secure PostgreSQL data archiving
    Odoo multi-company data offload
    Odoo cron job data archiving
    PostgreSQL external data storage
    Secure PostgreSQL data archiving
    Multi-database integration for offloading
    Batch data offloading system
    Asynchronous database offloading
    Data archiving with cron job automation
    Data indexing for fast retrieval
    
    ''',
    'description': '''
    Data Offload / External Archive Manager Module enables efficient offloading of large datasets from your primary database 
    to an external PostgreSQL database. With automated offload, retrieval, and purge options, this module enhances
    performance, reduces database size, and ensures seamless data management with advanced scheduling and security features.

    tus
    techultra
    techultra_private_limited_solution
    Data Offload 
    External Archive Manager
    Data Offload / External Archive Manager
    PostgreSQL 
    offloading,
    data archiving
    database optimization
    external storage solution
    data retrieval 
    scheduled purge 
    batch processing
    large dataset management
    PostgreSQL data offloading
    External database integration
    Data archiving solution
    Database offload for performance
    Large data management system
    External PostgreSQL storage solution
    Data lifecycle management
    Historical data archiving
    Scheduled data purge system
    Cron job data offloading
    Data retrieval from external databases
    Data retention management solution
    Database size reduction tool
    Offload database fields to external storage
    External database offload solution
    Offload large database fields to PostgreSQL
    Archive inactive data in external PostgreSQL
    Store historical records in external databases
    Retrieve archived data from external storage
    Automate data offloading and purging
    PostgreSQL archive storage for databases
    Data management for high-volume databases
    Performance optimization for databases
    Odoo PostgreSQL data offloading
    Odoo external database integration
    Database Restore
    Odoo data archiving module
    Odoo database offload solution
    Odoo performance optimization module
    Odoo large data management
    Odoo external PostgreSQL storage
    Odoo historical data archiving
    Odoo scheduled data purge
    Odoo cron-based data offload
    Odoo smart button data retrieval
    Odoo data retention management
    Odoo database size reduction
    Odoo offload selected fields
    Odoo external storage solution
    Offload Odoo model fields to PostgreSQL
    Archive old Odoo records in external database
    Reduce Odoo database size with PostgreSQL
    Store Odoo historical data externally
    Retrieve archived Odoo data on demand
    Automate Odoo data offloading and purge
    PostgreSQL archive database for Odoo
    PostgreSQL external data store
    Data lifecycle management for Odoo
    Odoo database scalability solution
    Secure PostgreSQL data archiving
    Odoo multi-company data offload
    Odoo cron job data archiving
    PostgreSQL external data storage
    Secure PostgreSQL data archiving
    Multi-database integration for offloading
    Batch data offloading system
    Asynchronous database offloading
    Data archiving with cron job automation
    Data indexing for fast retrieval
    ''',
    "depends": ["base",],
    "data": [
        "data/ir_cron.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/db_config_views.xml",
        "views/archive_config_views.xml",
        "views/menus.xml",

    ],
    'images': ['static/description/main_screen.gif'],
    'price': 49.00,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
}
