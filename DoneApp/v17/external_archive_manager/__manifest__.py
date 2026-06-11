# Part of Techultra Solutions. See LICENSE file for full copyright and licensing details.
{
    "name": "Odoo PostgreSQL Data Offloading | External Database Archiving Storage Management",
    "version": "17.0.0.0",
    "category": "Tools",
    'author': 'Techultra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    "summary": '''
    Odoo PostgreSQL Data Offloading helps businesses optimize database performance by moving selected record fields from the primary Odoo database to an external PostgreSQL database. The module securely archives data, reduces database size, and enables seamless retrieval whenever needed, ensuring efficient storage management and long-term scalability
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
    Odoo PostgreSQL Data Offloading is a powerful database optimization solution that allows businesses to offload selected fields from Odoo records to an external PostgreSQL database. Administrators can configure specific models and fields for archival based on business requirements. The module securely stores offloaded data externally while retaining record references within Odoo for seamless access. When needed, archived data can be automatically retrieved and restored to the original record. This helps reduce the size of the primary database, improve system performance, optimize storage usage, and support long-term data retention and compliance requirements.
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
    "depends": ["base", ],
    "data": [
        "data/ir_cron.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/db_config_views.xml",
        "views/archive_config_views.xml",
        "views/menus.xml",

    ],
    'images': ['static/description/main_screen.gif'],
    'price': 49.02,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
}
