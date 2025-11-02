import logging
import time
import uuid
from typing import Dict, Any
from .base_processor import BaseProcessor

logger = logging.getLogger(__name__)

class CreateDetailsProcessor(BaseProcessor):
    """Processor for create_details actions"""
    
    def _should_process(self, message: Dict[str, Any]) -> bool:
        """Check if this is a create_details message"""
        return message.get('action') == 'create_details'
    
    def _process_business_logic(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process create_details business logic"""
        try:
            logger.info(f"Processing create_details for ID: {message.get('id')}")
            
            # Simulate processing time
            time.sleep(0.12)
            
            # Extract relevant data from message
            request_id = message.get('id')
            create_data = message.get('data', {})
            
            # Validate required fields for creation
            required_fields = ['name']
            missing_fields = [field for field in required_fields if field not in create_data]
            
            if missing_fields:
                return {
                    'status': 'error',
                    'data': {'missing_fields': missing_fields},
                    'message': f'Missing required fields: {", ".join(missing_fields)}'
                }
            
            # Generate new record ID for the created resource
            new_record_id = str(uuid.uuid4())
            
            # Simulate database creation operation
            # In a real application, this would create a new database record
            created_record = {
                'id': new_record_id,
                'original_request_id': request_id,
                'name': create_data.get('name'),
                'description': create_data.get('description', f'New record: {create_data.get("name")}'),
                'category': create_data.get('category', 'general'),
                'created_date': time.strftime('%Y-%m-%dT%H:%M:%S'),
                'last_modified': time.strftime('%Y-%m-%dT%H:%M:%S'),
                'status': 'active',
                'version': 1,
                'metadata': {
                    'processed_by': 'create_details_processor',
                    'processing_time': time.time(),
                    'created_from': request_id,
                    'source_data': create_data
                }
            }
            
            # Simulate business rules validation
            validation_errors = []
            if len(create_data.get('name', '')) < 2:
                validation_errors.append('Name must be at least 2 characters long')
            
            if 'email' in create_data and '@' not in create_data['email']:
                validation_errors.append('Invalid email format')
            
            if validation_errors:
                return {
                    'status': 'error',
                    'data': {'validation_errors': validation_errors},
                    'message': 'Validation failed: ' + ', '.join(validation_errors)
                }
            
            # Add any additional computed fields
            created_record['computed_fields'] = {
                'slug': create_data.get('name', '').lower().replace(' ', '-'),
                'search_keywords': create_data.get('name', '').lower().split(),
                'creation_source': 'kafka_processor'
            }
            
            logger.info(f"Successfully created new record with ID: {new_record_id}")
            
            return {
                'status': 'success',
                'data': created_record,
                'message': f'Record created successfully with ID: {new_record_id}'
            }
            
        except Exception as e:
            logger.error(f"Error in create_details processing: {e}")
            return {
                'status': 'error',
                'data': {},
                'message': f'Failed to create details: {str(e)}'
            }