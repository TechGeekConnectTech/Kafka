import logging
import time
from typing import Dict, Any
from .base_processor import BaseProcessor

logger = logging.getLogger(__name__)

class UpdateDetailsProcessor(BaseProcessor):
    """Processor for update_details actions"""
    
    def _should_process(self, message: Dict[str, Any]) -> bool:
        """Check if this is an update_details message"""
        return message.get('action') == 'update_details'
    
    def _process_business_logic(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process update_details business logic"""
        try:
            logger.info(f"Processing update_details for ID: {message.get('id')}")
            
            # Simulate processing time
            time.sleep(0.15)
            
            # Extract relevant data from message
            record_id = message.get('id')
            update_data = message.get('data', {})
            
            # Validate update data
            if not update_data:
                return {
                    'status': 'error',
                    'data': {},
                    'message': 'No update data provided'
                }
            
            # Simulate database update operation
            # In a real application, this would update a database record
            updated_record = {
                'id': record_id,
                'name': update_data.get('name', f'Updated_Record_{record_id}'),
                'description': update_data.get('description', f'Updated description for record {record_id}'),
                'updated_fields': list(update_data.keys()),
                'last_modified': time.strftime('%Y-%m-%dT%H:%M:%S'),
                'status': update_data.get('status', 'updated'),
                'version': update_data.get('version', 1) + 1 if isinstance(update_data.get('version'), int) else 2,
                'metadata': {
                    'processed_by': 'update_details_processor',
                    'processing_time': time.time(),
                    'update_count': update_data.get('update_count', 0) + 1,
                    'original_data': update_data
                }
            }
            
            # Simulate validation checks
            validation_errors = []
            if 'name' in update_data and len(update_data['name']) < 2:
                validation_errors.append('Name must be at least 2 characters long')
            
            if validation_errors:
                return {
                    'status': 'error',
                    'data': {'validation_errors': validation_errors},
                    'message': 'Validation failed: ' + ', '.join(validation_errors)
                }
            
            logger.info(f"Successfully updated details for ID: {record_id}")
            
            return {
                'status': 'success',
                'data': updated_record,
                'message': f'Record updated successfully for ID: {record_id}. Updated fields: {", ".join(update_data.keys())}'
            }
            
        except Exception as e:
            logger.error(f"Error in update_details processing: {e}")
            return {
                'status': 'error',
                'data': {},
                'message': f'Failed to update details: {str(e)}'
            }