#!/usr/bin/env python3
"""
Duty Streaming Module for Monica
Implements streaming duties in batches to prevent Pico memory issues
"""

import asyncio
import time
from typing import List, Dict, Optional, Tuple, Iterator
from dataclasses import dataclass
from monica_pathing import Duty


@dataclass
class DutyBatch:
    """Represents a batch of duties to be streamed to the Pico"""
    duties: List[Dict]  # Serialized duties
    path_segment: List[int]  # Corresponding path positions
    batch_id: int
    start_time_ms: int
    end_time_ms: int
    duration_ms: int


class DutyStreamer:
    """
    Streams duties to Pico in manageable batches to prevent memory issues
    """
    
    def __init__(self, 
                 batch_size: int = 50,  # Number of duties per batch
                 buffer_size: int = 2,   # Number of batches to keep in buffer
                 lookahead_ms: int = 5000):  # How far ahead to prepare next batch
        self.batch_size = batch_size
        self.buffer_size = buffer_size
        self.lookahead_ms = lookahead_ms
        self.current_batch_id = 0
        
    def create_batches(self, duties: List[Duty], path: List[int]) -> List[DutyBatch]:
        """
        Split duties and path into manageable batches
        """
        if len(duties) != len(path) - 1:
            raise ValueError(f"Path length ({len(path)}) must be duties length + 1 ({len(duties) + 1})")
        
        batches = []
        
        for i in range(0, len(duties), self.batch_size):
            batch_duties = duties[i:i + self.batch_size]
            # Path needs one extra position for the final position after last duty
            batch_path = path[i:i + self.batch_size + 1]
            
            # Convert duties to dict format for JSON serialization
            duties_dict = [duty.to_dict() for duty in batch_duties]
            
            # Calculate timing for this batch
            start_time_ms = batch_duties[0].start_ms if batch_duties else 0
            end_time_ms = batch_duties[-1].end_ms if batch_duties else 0
            duration_ms = end_time_ms - start_time_ms
            
            batch = DutyBatch(
                duties=duties_dict,
                path_segment=batch_path,
                batch_id=self.current_batch_id,
                start_time_ms=start_time_ms,
                end_time_ms=end_time_ms,
                duration_ms=duration_ms
            )
            
            batches.append(batch)
            self.current_batch_id += 1
        
        print(f"Duty Streaming: Created {len(batches)} batches from {len(duties)} duties")
        print(f"Duty Streaming: Average batch size: {len(duties) / len(batches):.1f} duties")
        
        return batches
    
    def get_batch_for_time(self, batches: List[DutyBatch], current_time_ms: int) -> Optional[DutyBatch]:
        """
        Get the batch that should be playing at the given time
        """
        for batch in batches:
            if batch.start_time_ms <= current_time_ms <= batch.end_time_ms:
                return batch
        return None
    
    def get_next_batches(self, batches: List[DutyBatch], current_time_ms: int, count: int = None) -> List[DutyBatch]:
        """
        Get the next batches that should be loaded based on lookahead time
        """
        if count is None:
            count = self.buffer_size
        
        lookahead_time = current_time_ms + self.lookahead_ms
        next_batches = []
        
        for batch in batches:
            if batch.start_time_ms <= lookahead_time and len(next_batches) < count:
                next_batches.append(batch)
        
        return next_batches[:count]


class StreamingPicoClient:
    """
    Enhanced Pico client that supports streaming duties
    """
    
    def __init__(self, pico_client):
        self.pico_client = pico_client
        self.active_batches = {}  # batch_id -> batch
        self.loaded_batches = set()  # Set of loaded batch IDs
    
    def load_batch(self, batch: DutyBatch) -> bool:
        """
        Load a batch of duties to the Pico buffer
        """
        try:
            command = {
                "type": "load_duty_batch",
                "batch_id": batch.batch_id,
                "duties": batch.duties,
                "path_segment": batch.path_segment,
                "start_time_ms": batch.start_time_ms,
                "end_time_ms": batch.end_time_ms
            }
            
            response = self.pico_client.send_command(command)
            
            if response.get("success"):
                self.active_batches[batch.batch_id] = batch
                self.loaded_batches.add(batch.batch_id)
                print(f"Duty Streaming: Loaded batch {batch.batch_id} ({len(batch.duties)} duties)")
                return True
            else:
                print(f"Duty Streaming: Failed to load batch {batch.batch_id}: {response.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"Duty Streaming: Error loading batch {batch.batch_id}: {e}")
            return False
    
    def unload_batch(self, batch_id: int) -> bool:
        """
        Unload a batch from Pico memory to free space
        """
        try:
            command = {
                "type": "unload_duty_batch",
                "batch_id": batch_id
            }
            
            response = self.pico_client.send_command(command)
            
            if response.get("success"):
                if batch_id in self.active_batches:
                    del self.active_batches[batch_id]
                self.loaded_batches.discard(batch_id)
                print(f"Duty Streaming: Unloaded batch {batch_id}")
                return True
            else:
                print(f"Duty Streaming: Failed to unload batch {batch_id}: {response.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"Duty Streaming: Error unloading batch {batch_id}: {e}")
            return False
    
    def start_streaming_performance(self, song_name: str, total_batches: int) -> bool:
        """
        Start a streaming performance on the Pico
        """
        try:
            command = {
                "type": "start_streaming_performance",
                "song": song_name,
                "total_batches": total_batches
            }
            
            response = self.pico_client.send_command(command)
            
            if response.get("success"):
                print(f"Duty Streaming: Started streaming performance '{song_name}' with {total_batches} batches")
                return True
            else:
                print(f"Duty Streaming: Failed to start streaming performance: {response.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"Duty Streaming: Error starting streaming performance: {e}")
            return False
    
    def play_batch(self, batch_id: int) -> bool:
        """
        Tell Pico to start playing a specific batch
        """
        try:
            command = {
                "type": "play_duty_batch",
                "batch_id": batch_id
            }
            
            response = self.pico_client.send_command(command)
            
            if response.get("success"):
                print(f"Duty Streaming: Started playing batch {batch_id}")
                return True
            else:
                print(f"Duty Streaming: Failed to play batch {batch_id}: {response.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"Duty Streaming: Error playing batch {batch_id}: {e}")
            return False
    
    def get_streaming_status(self) -> Dict:
        """
        Get current streaming status from Pico
        """
        try:
            command = {"type": "streaming_status"}
            response = self.pico_client.send_command(command)
            
            return response if response.get("success") else {}
            
        except Exception as e:
            print(f"Duty Streaming: Error getting streaming status: {e}")
            return {}


class StreamingController:
    """
    Controls the streaming of duties to Pico during performance
    """
    
    def __init__(self, streamer: DutyStreamer, pico_client: StreamingPicoClient):
        self.streamer = streamer
        self.pico_client = pico_client
        self.is_streaming = False
        self.current_batch_index = 0
    
    async def stream_performance(self, song_name: str, duties: List[Duty], path: List[int]) -> bool:
        """
        Execute a complete streaming performance
        """
        try:
            # Create batches
            batches = self.streamer.create_batches(duties, path)
            
            if not batches:
                print("Duty Streaming: No batches created")
                return False
            
            # Start streaming performance on Pico
            if not self.pico_client.start_streaming_performance(song_name, len(batches)):
                return False
            
            # Load initial buffer of batches
            initial_batches = batches[:self.streamer.buffer_size]
            for batch in initial_batches:
                if not self.pico_client.load_batch(batch):
                    print(f"Duty Streaming: Failed to load initial batch {batch.batch_id}")
                    return False
            
            # Start performance
            self.is_streaming = True
            performance_start_time = time.time() * 1000  # Convert to milliseconds
            
            print(f"Duty Streaming: Starting performance with {len(batches)} batches")
            
            # Stream batches during performance
            for i, batch in enumerate(batches):
                if not self.is_streaming:
                    break
                
                # Play current batch
                if not self.pico_client.play_batch(batch.batch_id):
                    print(f"Duty Streaming: Failed to play batch {batch.batch_id}")
                    break
                
                # Load next batch while current one is playing
                next_batch_index = i + self.streamer.buffer_size
                if next_batch_index < len(batches):
                    next_batch = batches[next_batch_index]
                    self.pico_client.load_batch(next_batch)
                
                # Unload old batch to free memory
                old_batch_index = i - self.streamer.buffer_size
                if old_batch_index >= 0:
                    old_batch = batches[old_batch_index]
                    self.pico_client.unload_batch(old_batch.batch_id)
                
                # Wait for batch to complete
                await asyncio.sleep(batch.duration_ms / 1000.0)
            
            print("Duty Streaming: Performance completed")
            return True
            
        except Exception as e:
            print(f"Duty Streaming: Error during streaming performance: {e}")
            return False
        finally:
            self.is_streaming = False
    
    def stop_streaming(self):
        """Stop the current streaming performance"""
        self.is_streaming = False
        print("Duty Streaming: Performance stopped")


# Example usage and testing
if __name__ == "__main__":
    # This would be used in the main application
    print("Duty Streaming Module - Ready for integration")
    
    # Example configuration
    streamer = DutyStreamer(
        batch_size=50,      # 50 duties per batch (much more manageable for Pico)
        buffer_size=3,      # Keep 3 batches in memory (current + 2 lookahead)
        lookahead_ms=5000   # Prepare next batch 5 seconds ahead
    )
    
    print(f"Configured streaming with {streamer.batch_size} duties per batch")
    print(f"Buffer size: {streamer.buffer_size} batches")
    print(f"Lookahead time: {streamer.lookahead_ms}ms")

