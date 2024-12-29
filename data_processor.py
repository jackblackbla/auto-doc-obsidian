class DataProcessor:
    def __init__(self):
        self.data = []
        self.processed = False
    
    def add_data(self, item):
        """Add a single data item"""
        self.data.append(item)
        self.processed = False
    
    def process_all(self):
        """Process all data items"""
        if self.processed:
            return
            
        self.data = [str(item).upper() for item in self.data]
        self.processed = True
    
    def get_results(self):
        """Get processed results"""
        if not self.processed:
            self.process_all()
        return self.data