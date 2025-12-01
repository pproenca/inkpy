"""
Instances registry - stores Ink instances per stdout stream
"""
from typing import Dict, Optional, TextIO

class Instances:
    """Registry of Ink instances per stdout stream"""
    
    def __init__(self):
        self._instances: Dict[int, 'Ink'] = {}
    
    def get(self, stdout: TextIO) -> Optional['Ink']:
        """Get Ink instance for stdout"""
        return self._instances.get(id(stdout))
    
    def set(self, stdout: TextIO, ink: 'Ink'):
        """Register Ink instance for stdout"""
        self._instances[id(stdout)] = ink
    
    def delete(self, stdout: TextIO):
        """Remove Ink instance for stdout"""
        self._instances.pop(id(stdout), None)

instances = Instances()

