import cv2
import numpy as np
import os
import math
import subprocess
import tempfile
import shutil
import sys
import re
import hashlib
from collections import Counter

class YouTubeEncoder:
    def __init__(self, key=None):
        self.width = 1920
        self.height = 1080
        self.fps = 6
        
        # Parameters
        self.block_height = 16
        self.block_width = 24
        self.spacing = 4
        
        # Encryption key
        self.key = key
        self.use_encryption = key is not None
        
        # 16 colors
        self.colors = {
            '0000': (255, 0, 0),      # Bright blue
            '0001': (0, 255, 0),      # Bright green
            '0010': (0, 0, 255),      # Bright red
            '0011': (255, 255, 0),    # Yellow
            '0100': (255, 0, 255),    # Purple
            '0101': (0, 255, 255),    # Blue
            '0110': (255, 128, 0),    # Orange
            '0111': (128, 0, 255),    # Purple
            '1000': (0, 128, 128),    # Turquoise
            '1001': (128, 128, 0),    # Olive
            '1010': (128, 0, 128),    # Dark purple
            '1011': (0, 128, 0),      # Dark green
            '1100': (128, 0, 0),      # Burgundy
            '1101': (0, 0, 128),      # Dark blue
            '1110': (192, 192, 192),  # Light gray
            '1111': (255, 255, 255)   # White
        }
        
        # Markers at the corners
        self.marker_size = 80
        
        # Grid calculation
        self.blocks_x = (self.width - 2*self.marker_size) // (self.block_width + self.spacing)
        self.blocks_y = (self.height - 2*self.marker_size) // (self.block_height + self.spacing)
        self.blocks_per_region = self.blocks_x * self.blocks_y
        self.blocks_per_frame = self.blocks_per_region * 3
        
        # End marker
        self.eof_marker = "█" * 64
        self.eof_bytes = self.eof_marker.encode('utf-8')
        
        print("="*60)
        print("🎬 CODER (6 FPS)")
        print("="*60)
        print(f"📊 Grid: {self.blocks_x} x {self.blocks_y} blocks per region")
        print(f"🎞️  FPS: {self.fps}")
        print(f"🔐 Encryption: {'ON' if self.use_encryption else 'OFF'}")
    
    def _encrypt_data(self, data):
        """XOR encryption with a key"""
        if not self.use_encryption:
            return data
        
        key_bytes = self.key.encode()
        result = bytearray()
        
        for i, byte in enumerate(data):
            key_byte = key_bytes[i % len(key_bytes)]
            result.append(byte ^ key_byte)
        
        return result
    
    def _draw_markers(self, frame):
        """Draws markers in the corners"""
        cv2.rectangle(frame, (0, 0), (self.marker_size, self.marker_size), (255, 255, 255), -1)
        cv2.rectangle(frame, (self.width-self.marker_size, 0), (self.width, self.marker_size), (255, 255, 255), -1)
        cv2.rectangle(frame, (0, self.height-self.marker_size), (self.marker_size, self.height), (255, 255, 255), -1)
        cv2.rectangle(frame, (self.width-self.marker_size, self.height-self.marker_size), (self.width, self.height), (255, 255, 255), -1)
        
        cv2.rectangle(frame, (0, 0), (self.marker_size, self.marker_size), (0, 0, 0), 2)
        cv2.rectangle(frame, (self.width-self.marker_size, 0), (self.width, self.marker_size), (0, 0, 0), 2)
        cv2.rectangle(frame, (0, self.height-self.marker_size), (self.marker_size, self.height), (0, 0, 0), 2)
        cv2.rectangle(frame, (self.width-self.marker_size, self.height-self.marker_size), (self.width, self.height), (0, 0, 0), 2)
        
        return frame
    
    def _draw_block(self, frame, x, y, color):
        """Draws one block"""
        x1 = self.marker_size + x * (self.block_width + self.spacing)
        y1 = self.marker_size + y * (self.block_height + self.spacing)
        x2 = x1 + self.block_width
        y2 = y1 + self.block_height
        
        if x2 > self.width - self.marker_size or y2 > self.height - self.marker_size:
            return False
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, -1)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 1)
        return True
    
    def _bits_to_color(self, bits):
        """4 bits -> color"""
        while len(bits) < 4:
            bits = '0' + bits
        return self.colors.get(bits, (255, 0, 0))
    
    def _data_to_blocks(self, data):
        """Converts data into 4-bit blocks"""
        all_bits = []
        for byte in data:
            for i in range(7, -1, -1):
                all_bits.append(str((byte >> i) & 1))
        
        while len(all_bits) % 4 != 0:
            all_bits.append('0')
        
        blocks = [''.join(all_bits[i:i+4]) for i in range(0, len(all_bits), 4)]
        return blocks
    
    def encode(self, input_file, output_file):
        """Encodes a file into video with optional encryption"""
        
        print("\n📤 FILE ENCODING")
        print("-" * 40)
        
        # Reading the file
        with open(input_file, 'rb') as f:
            data = f.read()
        
        print(f"📄 File: {input_file}")
        print(f"📦 Size: {len(data)} байт")
        
        # encrypt data if necessary.
        if self.use_encryption:
            encrypted_data = self._encrypt_data(data)
            print(f"🔐 The data is encrypted")
        else:
            encrypted_data = data
        
        # Create a title
        header = f"FILE:{os.path.basename(input_file)}:SIZE:{len(data)}|"
        header_bytes = header.encode('latin-1')
        print(f"📋 Title: {header}")
        
        # Converting into blocks
        header_blocks = self._data_to_blocks(header_bytes)
        data_blocks = self._data_to_blocks(encrypted_data)
        eof_blocks = self._data_to_blocks(self.eof_bytes)
        all_blocks = header_blocks + data_blocks + eof_blocks
        
        print(f"🎨 Total blocks: {len(all_blocks)}")
        print(f"🏁 End marker: {len(eof_blocks)} blocks")
        
        # Calculating the number of frames
        frames_needed = math.ceil(len(all_blocks) / self.blocks_per_region)
        # Add 5 protective frames
        frames_needed += 5
        print(f"🎬 Frames required: {frames_needed}")
        print(f"⏱️  Video length: {frames_needed/self.fps:.1f} sec")
        
        # Create a temporary folder
        temp_dir = tempfile.mkdtemp()
        print(f"📁 Temporary folder: {temp_dir}")
        
        # Creating frames
        for frame_num in range(frames_needed - 5):
            print(f"\n🖼️  Frame {frame_num + 1}/{frames_needed}")
            
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            frame = self._draw_markers(frame)
            
            start_idx = frame_num * self.blocks_per_region
            end_idx = min(start_idx + self.blocks_per_region, len(all_blocks))
            frame_blocks = all_blocks[start_idx:end_idx]
            
            # Main blocks
            for idx, bits in enumerate(frame_blocks):
                y = idx // self.blocks_x
                x = idx % self.blocks_x
                if y < self.blocks_y:
                    color = self._bits_to_color(bits)
                    self._draw_block(frame, x, y, color)
            
            # Reserve 1
            for idx, bits in enumerate(frame_blocks):
                y = idx // self.blocks_x
                x = idx % self.blocks_x + self.blocks_x
                if x < self.blocks_x * 2 and y < self.blocks_y:
                    color = self._bits_to_color(bits)
                    self._draw_block(frame, x, y, color)
            
            # Reserve 2
            for idx, bits in enumerate(frame_blocks):
                y = idx // self.blocks_x + self.blocks_y
                x = idx % self.blocks_x
                if x < self.blocks_x and y < self.blocks_y * 2:
                    color = self._bits_to_color(bits)
                    self._draw_block(frame, x, y, color)
            
            # Save the frame
            frame_file = os.path.join(temp_dir, f"frame_{frame_num:05d}.png")
            cv2.imwrite(frame_file, frame)
        
        # Create protective frames (blue background)
        print("\n🛡️  Creating protective frames...")
        for i in range(5):
            frame_num = frames_needed - 5 + i
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            frame = self._draw_markers(frame)
            for y in range(self.blocks_y * 2):
                for x in range(self.blocks_x * 2):
                    self._draw_block(frame, x, y, (255, 0, 0))
            frame_file = os.path.join(temp_dir, f"frame_{frame_num:05d}.png")
            cv2.imwrite(frame_file, frame)
            print(f"  🟦 Protective frame {i+1}/5")
        
        # Convert to MP4
        print("\n🎞️  Convert to MP4...")
        
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            
            cmd = [
                'ffmpeg',
                '-framerate', str(self.fps),
                '-i', os.path.join(temp_dir, 'frame_%05d.png'),
                '-c:v', 'libx264',
                '-preset', 'slow',
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                '-an',
                '-movflags', '+faststart',
                '-y',
                output_file
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            print("✅ FFmpeg conversion successful")
            
        except Exception as e:
            print(f"⚠️ FFmpeg is not available, using OpenCV...")
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_file, fourcc, self.fps, (self.width, self.height))
            
            for frame_num in range(frames_needed):
                frame_file = os.path.join(temp_dir, f"frame_{frame_num:05d}.png")
                frame = cv2.imread(frame_file)
                if frame is not None:
                    out.write(frame)
            out.release()
        
        # Deleting temporary files
        shutil.rmtree(temp_dir)
        print("🧹 Temporary files have been deleted.")
        
        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            print(f"\n✅ The video has been saved.: {output_file}")
            print(f"📊 Size: {size} byte ({size/1024/1024:.2f} MB)")
            print(f"🎬 Frames: {frames_needed}")
            print(f"⏱️  Duration: {frames_needed/self.fps:.1f} sec")
            return True
        return False


class YouTubeDecoder:
    def __init__(self, key=None):
        self.width = 1920
        self.height = 1080
        self.block_height = 16
        self.block_width = 24
        self.spacing = 4
        self.marker_size = 80
        
        # Encryption key
        self.key = key
        
        # 16 colors
        self.colors = {
            '0000': (255, 0, 0),
            '0001': (0, 255, 0),
            '0010': (0, 0, 255),
            '0011': (255, 255, 0),
            '0100': (255, 0, 255),
            '0101': (0, 255, 255),
            '0110': (255, 128, 0),
            '0111': (128, 0, 255),
            '1000': (0, 128, 128),
            '1001': (128, 128, 0),
            '1010': (128, 0, 128),
            '1011': (0, 128, 0),
            '1100': (128, 0, 0),
            '1101': (0, 0, 128),
            '1110': (192, 192, 192),
            '1111': (255, 255, 255)
        }
        
        # Optimizations
        self.color_values = np.array(list(self.colors.values()), dtype=np.int32)
        self.color_keys = list(self.colors.keys())
        self.color_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Grid calculation
        self.blocks_x = (self.width - 2*self.marker_size) // (self.block_width + self.spacing)
        self.blocks_y = (self.height - 2*self.marker_size) // (self.block_height + self.spacing)
        self.blocks_per_region = self.blocks_x * self.blocks_y
        
        # Pre-calculation of coordinates
        self._precompute_coordinates()
        
        print("="*60)
        print("🎬 DECODER")
        print("="*60)
        print(f"📊 grid: {self.blocks_x} x {self.blocks_y} blocks")
        print(f"🔐 Key: {'yes' if self.key else 'no'}")
    
    def _precompute_coordinates(self):
        """Pre-calculates block coordinates"""
        self.block_coords = []
        for idx in range(self.blocks_per_region):
            y = idx // self.blocks_x
            x = idx % self.blocks_x
            if y < self.blocks_y:
                cx = self.marker_size + x * (self.block_width + self.spacing) + self.block_width // 2
                cy = self.marker_size + y * (self.block_height + self.spacing) + self.block_height // 2
                self.block_coords.append((cx, cy))
    
    def _decrypt_data(self, data):
        """XOR decryption with key"""
        if not self.key:
            return data
        
        key_bytes = self.key.encode()
        result = bytearray()
        
        for i, byte in enumerate(data):
            key_byte = key_bytes[i % len(key_bytes)]
            result.append(byte ^ key_byte)
        
        return result
    
    def _color_to_bits_fast(self, color):
        """Optimized color search"""
        color_key = (color[0], color[1], color[2])
        
        if color_key in self.color_cache:
            self.cache_hits += 1
            return self.color_cache[color_key]
        
        self.cache_misses += 1
        
        # Quick check for blue background
        if color[0] > 200 and color[1] < 50 and color[2] < 50:
            self.color_cache[color_key] = '0000'
            return '0000'
        
        # NumPy vectorization
        color_arr = np.array([color[0], color[1], color[2]], dtype=np.int32)
        distances = np.sum((self.color_values - color_arr) ** 2, axis=1)
        best_idx = np.argmin(distances)
        result = self.color_keys[best_idx]
        
        self.color_cache[color_key] = result
        return result
    
    def decode_frame_fast(self, frame):
        """Fast single frame decoding with scaling"""
        # Force scaling to original size
        if frame.shape[1] != self.width or frame.shape[0] != self.height:
            frame = cv2.resize(frame, (self.width, self.height), 
                              interpolation=cv2.INTER_NEAREST)
        
        blocks = []
        h, w = frame.shape[:2]
        
        for cx, cy in self.block_coords:
            if cx < w and cy < h:
                color = frame[cy, cx]
                bits = self._color_to_bits_fast(color)
                blocks.append(bits)
            else:
                blocks.append('0000')
        
        return blocks
    
    def _blocks_to_bytes(self, blocks):
        """4-bit blocks -> bytes"""
        all_bits = ''.join(blocks)
        bytes_data = bytearray()
        
        for i in range(0, len(all_bits) - 7, 8):
            byte_str = all_bits[i:i+8]
            if len(byte_str) == 8:
                try:
                    byte = int(byte_str, 2)
                    bytes_data.append(byte)
                except:
                    bytes_data.append(0)
        
        return bytes_data
    
    def _find_eof_marker(self, data):
        """Searching for end-of-█████ marker... in data"""
        eof_bytes = b'\xe2\x96\x88' * 64
        
        for i in range(len(data) - len(eof_bytes)):
            if data[i:i+len(eof_bytes)] == eof_bytes:
                return i
        return -1
    
    def decode(self, video_file, output_dir='.'):
        """Decodes video"""
        
        print("\n📥 VIDEO DECODING")
        print("-" * 40)
        
        if not os.path.exists(video_file):
            print(f"❌ File not found: {video_file}")
            return False
        
        cap = cv2.VideoCapture(video_file)
        if not cap.isOpened():
            print("❌ Failed to open video")
            return False
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"📹 Total frames: {total_frames}")
        print(f"📹 FPS: {fps}")
        print(f"📹 resolution: {width}x{height}")
        
        # Reset statistics
        self.cache_hits = 0
        self.cache_misses = 0
        start_time = cv2.getTickCount()
        
        # Block collection
        all_blocks = []
        frames_processed = 0
        
        for frame_num in range(total_frames):
            ret, frame = cap.read()
            if not ret:
                break
            
            frames_processed += 1
            
            # Progress
            if frame_num % 100 == 0:
                elapsed = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
                speed = frames_processed / elapsed if elapsed > 0 else 0
                cache_ratio = (self.cache_hits / (self.cache_hits + self.cache_misses) * 100) if (self.cache_hits + self.cache_misses) > 0 else 0
                print(f"  Progress: {frame_num}/{total_frames} | "
                      f"Speed: {speed:.1f} frames per second | "
                      f"Cache: {cache_ratio:.1f}%")
            
            # Frame decoding with scaling
            frame_blocks = self.decode_frame_fast(frame)
            all_blocks.extend(frame_blocks)
        
        cap.release()
        
        # Statistics
        elapsed = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
        print(f"\n📊 Statistics: {len(all_blocks)} blocks for {elapsed:.1f} sec")
        print(f"  🎯 Cache: hits {self.cache_hits}, misses {self.cache_misses}")
        print(f"  🔄 Frames processed: {frames_processed}")
        
        # Convert to bytes
        bytes_data = self._blocks_to_bytes(all_blocks)
        print(f"📦 Bytes received: {len(bytes_data)}")
        
        # Finding the end marker
        eof_pos = self._find_eof_marker(bytes_data)
        if eof_pos > 0:
            bytes_data = bytes_data[:eof_pos]
            print(f"✅ End marker found at position {eof_pos}")
            print(f"📦 Byte after trimming: {len(bytes_data)}")
        else:
            print("⚠️ End marker not found")
        
        # Search for a title
        data_str = bytes_data[:1000].decode('latin-1', errors='ignore')
        pattern = r'FILE:([^:]+):SIZE:(\d+)\|'
        match = re.search(pattern, data_str)
        
        if match:
            filename = match.group(1)
            filesize = int(match.group(2))
            
            print(f"\n✅ Found title: {filename}, размер: {filesize} байт")
            
            header_str = match.group(0)
            header_bytes = header_str.encode('latin-1')
            header_pos = bytes_data.find(header_bytes)
            
            if header_pos >= 0:
                # Extracting encrypted data
                encrypted_data = bytes_data[header_pos + len(header_bytes):header_pos + len(header_bytes) + filesize]
                
                # We decrypt if there is a key.
                if self.key:
                    file_data = self._decrypt_data(encrypted_data)
                    print(f"🔓 The data has been decrypted.")
                else:
                    file_data = encrypted_data
                    print(f"⚠️ Data without decryption")
                
                # Save the file
                output_path = os.path.join(output_dir, filename)
                counter = 1
                base, ext = os.path.splitext(filename)
                while os.path.exists(output_path):
                    output_path = os.path.join(output_dir, f"{base}_{counter}{ext}")
                    counter += 1
                
                with open(output_path, 'wb') as f:
                    f.write(file_data)
                
                print(f"\n✅ File recovered: {output_path}")
                print(f"📏 Size: {len(file_data)} byte")
                
                # Size check
                if len(file_data) == filesize:
                    print("✅ The size matches the original")
                else:
                    print(f"⚠️ The size does not match: {len(file_data)} != {filesize}")
                
                return True
        else:
            print("❌ Title not found")
        
        # If didn't find the title
        output_path = os.path.join(output_dir, "decoded_data.bin")
        with open(output_path, 'wb') as f:
            f.write(bytes_data)
        print(f"\n💾 Data saved: {output_path}")
        return False


def read_key_from_file(key_file='key.txt'):
    """Reads the key from the key.txt file"""
    try:
        if os.path.exists(key_file):
            with open(key_file, 'r', encoding='utf-8') as f:
                key = f.read().strip()
                if key:
                    print(f"🔑 Key loaded from {key_file}")
                    return key
                else:
                    print(f"⚠️ File {key_file} empty")
        else:
            print(f"ℹ️ File {key_file} not found, encryption not used")
    except Exception as e:
        print(f"⚠️ Error reading key: {e}")
    
    return None


def main():
    if len(sys.argv) < 2:
        print("\n" + "="*60)
        print("🎥(6 FPS)")
        print("="*60)
        print("\nUsage:")
        print("  encode <file> [output.mp4] - encode file")
        print("  decode <video> [folder] - decode video")
        print("\nSpecifications:")
        print("  • Frame rate: 6 FPS")
        print("  • Scaling to 1920x1080")
        print("  • End of data marker")
        print("  • 5 protective frames")
        print("\nШифрование:")
        print("  • To encrypt, create key.txt with the key")
        return
    
    # Reading the key from the file
    key = read_key_from_file()
    
    if sys.argv[1] == "encode":
        encoder = YouTubeEncoder(key)
        input_file = sys.argv[2]
        output = sys.argv[3] if len(sys.argv) > 3 else "output.mp4"
        encoder.encode(input_file, output)
        
    elif sys.argv[1] == "decode":
        decoder = YouTubeDecoder(key)
        video_file = sys.argv[2]
        output_dir = sys.argv[3] if len(sys.argv) > 3 else "."
        decoder.decode(video_file, output_dir)
    else:
        print(f"❌ Unknown command: {sys.argv[1]}")


if __name__ == "__main__":
    main()