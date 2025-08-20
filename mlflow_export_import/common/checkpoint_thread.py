import threading
import time
from datetime import datetime
import os
import pandas as pd
import logging
import pyarrow.dataset as ds
from mlflow_export_import.common import utils
from mlflow_export_import.common import filesystem as _fs
from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()

_logger = utils.getLogger(__name__)

class CheckpointThread(threading.Thread):   #birbal added 
    def __init__(self, queue, checkpoint_dir, interval=300, batch_size=100):
        super().__init__()
        self.queue = queue
        self.checkpoint_dir = checkpoint_dir
        self.interval = interval
        self.batch_size = batch_size
        self._stop_event = threading.Event()
        self._buffer = []
        self._last_flush_time = time.time()


    def run(self):
        max_drain_batch = 50  # Max items to pull per loop iteration
        while not self._stop_event.is_set() or not self.queue.empty():
            items_fetched = False
            drain_count = 0

            try:
                while not self.queue.empty():
                    _logger.debug(f"drain_count is {drain_count} and buffer len is {len(self._buffer)}")
                    item = self.queue.get()
                    self._buffer.append(item)
                    drain_count += 1
                    if drain_count > max_drain_batch:   
                        _logger.info(f" drain_count > max_drain_batch is TRUE")                     
                        items_fetched = True
                        break
                    
            except Exception:
                pass  # Queue is empty or bounded

            if items_fetched:
                _logger.info(f"[Checkpoint] Fetched {drain_count} items from queue.")

            time_since_last_flush = time.time() - self._last_flush_time
            if len(self._buffer) >= self.batch_size or time_since_last_flush >= self.interval:
                _logger.info(f"ready to flush to delta")
                self.flush_to_delta()
                self._buffer.clear()
                self._last_flush_time = time.time()

        # Final flush
        if self._buffer:
            self.flush_to_delta()
            self._buffer.clear()



    def flush_to_delta(self):
        _logger.info(f"flush_to_delta called")
        try:
            df = pd.DataFrame(self._buffer)
            if df.empty:
                _logger.info(f"[Checkpoint] DataFrame is empty. Skipping write to {self.checkpoint_dir}")
                return

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(self.checkpoint_dir, f"checkpoint_{timestamp}.parquet")
            df.to_parquet(file_path, index=False)
            _logger.info(f"[Checkpoint] Saved len(df) {len(df)} records to {file_path}")
            
        except Exception as e:
            _logger.error(f"[Checkpoint] Failed to write to {self.checkpoint_dir}: {e}", exc_info=True)

    def stop(self):        
        self._stop_event.set()
        _logger.info("STOP event called.")

    @staticmethod
    def load_processed_objects(checkpoint_dir, object_type= None):
        try:
            dataset = ds.dataset(checkpoint_dir, format="parquet")
            df = dataset.to_table().to_pandas()
            result_list = []

            if df.empty:
                _logger.warning(f"[Checkpoint] Parquet data is empty in {checkpoint_dir}")
                return {}

            if object_type == "experiments":
                result_list = df["experiment_id"].dropna().unique().tolist()

            if object_type == "models":
                result_list = df["model"].dropna().unique().tolist()
                
            return result_list

        except Exception as e:
            _logger.warning(f"[Checkpoint] Failed to load checkpoint data from {checkpoint_dir}: {e}", exc_info=True)
            return None

def filter_unprocessed_objects(checkpoint_dir,object_type,to_be_processed_objects):       #birbal added         
        processed_objects = CheckpointThread.load_processed_objects(checkpoint_dir,object_type)
        if isinstance(to_be_processed_objects, dict):   
            unprocessed_objects = {k: v for k, v in to_be_processed_objects.items() if k not in processed_objects}
            return unprocessed_objects
        
        if isinstance(to_be_processed_objects, list):   
            unprocessed_objects = list(set(to_be_processed_objects) - set(processed_objects))
            return unprocessed_objects
        
        return None
              
             