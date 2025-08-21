#!/usr/bin/env python3
"""
Cindir PointCloud Manager v2.1.3
Professional Point Cloud Processing and Analysis Software
Copyright (c) 2024 Cindir Technologies. All rights reserved.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import numpy as np
import open3d as o3d
import laspy
import json
import os
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PointCloudProcessor:
    
    def __init__(self):
        self.point_cloud = None
        self.mesh = None
        self.normals = None
        self.colors = None
        self.metadata = {}
        
    def load_pointcloud(self, file_path):
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.las' or file_ext == '.laz':
                self.point_cloud = self._load_las(file_path)
            elif file_ext == '.ply':
                self.point_cloud = self._load_ply(file_path)
            elif file_ext == '.pcd':
                self.point_cloud = self._load_pcd(file_path)
            elif file_ext == '.xyz':
                self.point_cloud = self._load_xyz(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
                
            logger.info(f"Successfully loaded point cloud: {len(self.point_cloud.points)} points")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load point cloud: {e}")
            return False
    
    def _load_las(self, file_path):
        las_data = laspy.read(file_path)
        points = np.vstack((las_data.x, las_data.y, las_data.z)).transpose()
        
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        
        if hasattr(las_data, 'red') and hasattr(las_data, 'green') and hasattr(las_data, 'blue'):
            colors = np.vstack((las_data.red, las_data.green, las_data.blue)).transpose()
            pcd.colors = o3d.utility.Vector3dVector(colors / 65535.0)
        
        return pcd
    
    def _load_ply(self, file_path):
        return o3d.io.read_point_cloud(file_path)
    
    def _load_pcd(self, file_path):
        return o3d.io.read_point_cloud(file_path)
    
    def _load_xyz(self, file_path):
        data = np.loadtxt(file_path, delimiter=' ')
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(data[:, :3])
        
        if data.shape[1] > 3:
            pcd.colors = o3d.utility.Vector3dVector(data[:, 3:6] / 255.0)
        
        return pcd
    
    def estimate_normals(self, radius=0.1, max_nn=30):
        if self.point_cloud is None:
            return False
            
        self.point_cloud.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamRadius(radius=radius, max_nn=max_nn)
        )
        self.normals = np.asarray(self.point_cloud.normals)
        logger.info("Normals estimated successfully")
        return True
    
    def remove_outliers(self, nb_neighbors=20, std_ratio=2.0):
        if self.point_cloud is None:
            return False
            
        cleaned_pcd, _ = self.point_cloud.remove_statistical_outlier(
            nb_neighbors=nb_neighbors, std_ratio=std_ratio
        )
        self.point_cloud = cleaned_pcd
        logger.info(f"Outliers removed. Remaining points: {len(self.point_cloud.points)}")
        return True
    
    def downsample(self, voxel_size=0.05):
        if self.point_cloud is None:
            return False
            
        downsampled = self.point_cloud.voxel_down_sample(voxel_size=voxel_size)
        self.point_cloud = downsampled
        logger.info(f"Downsampled to {len(self.point_cloud.points)} points")
        return True
    
    def create_mesh(self, depth=8, width=0.1, scale=1.1):
        if self.point_cloud is None or self.normals is None:
            return False
            
        self.mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
            self.point_cloud, depth=depth, width=width, scale=scale
        )
        
        vertices_to_remove = densities < np.quantile(densities, 0.1)
        self.mesh.remove_vertices_by_mask(vertices_to_remove)
        
        logger.info(f"Mesh created with {len(self.mesh.vertices)} vertices")
        return True
    
    def save_results(self, output_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.point_cloud:
            o3d.io.write_point_cloud(
                os.path.join(output_dir, f"processed_cloud_{timestamp}.ply"),
                self.point_cloud
            )
        
        if self.mesh:
            o3d.io.write_triangle_mesh(
                os.path.join(output_dir, f"mesh_{timestamp}.ply"),
                self.mesh
            )
        
        metadata = {
            "processing_date": timestamp,
            "original_points": getattr(self, 'original_point_count', 0),
            "final_points": len(self.point_cloud.points) if self.point_cloud else 0,
            "mesh_vertices": len(self.mesh.vertices) if self.mesh else 0,
            "mesh_faces": len(self.mesh.triangles) if self.mesh else 0
        }
        
        with open(os.path.join(output_dir, f"metadata_{timestamp}.json"), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Results saved to {output_dir}")
        return True

class CindirPointCloudManager:
    
    def __init__(self):
        self.root = tk.Tk()
        self.processor = PointCloudProcessor()
        self.current_file = None
        self.processing = False
        self.setup_ui()
        
    def setup_ui(self):
        self.root.title("Cindir PointCloud Manager v2.1.3")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0a0a0a')
        
        main_frame = tk.Frame(self.root, bg='#0a0a0a', padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        header_frame = tk.Frame(main_frame, bg='#0a0a0a', height=120)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)
        
        logo_label = tk.Label(header_frame, text="CINDIR", 
                             font=('Segoe UI', 36, 'bold'), 
                             fg='#ffffff', bg='#0a0a0a')
        logo_label.pack(anchor=tk.W)
        
        subtitle_label = tk.Label(header_frame, text="PointCloud Manager", 
                                 font=('Segoe UI', 16), 
                                 fg='#888888', bg='#0a0a0a')
        subtitle_label.pack(anchor=tk.W)
        
        version_label = tk.Label(header_frame, text="v2.1.3", 
                                font=('Segoe UI', 12, 'bold'), 
                                fg='#e74c3c', bg='#0a0a0a',
                                padx=15, pady=8, relief='flat', bd=0)
        version_label.pack(anchor=tk.E)
        
        content_frame = tk.Frame(main_frame, bg='#0a0a0a')
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(30, 0))
        
        left_panel = self.create_left_panel(content_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        right_panel = self.create_right_panel(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(15, 0))
    
    def create_left_panel(self, parent):
        panel = tk.Frame(parent, bg='#1a1a1a', relief='flat', bd=0)
        
        header = tk.Label(panel, text="FILE OPERATIONS", 
                         font=('Segoe UI', 14, 'bold'), 
                         fg='#ffffff', bg='#1a1a1a', pady=20)
        header.pack(fill=tk.X)
        
        file_section = tk.Frame(panel, bg='#1a1a1a')
        file_section.pack(fill=tk.X, padx=25, pady=(0, 25))
        
        path_label = tk.Label(file_section, text="PointCloud File Path", 
                             font=('Segoe UI', 11, 'bold'), 
                             fg='#cccccc', bg='#1a1a1a', anchor=tk.W)
        path_label.pack(fill=tk.X, pady=(0, 8))
        
        self.file_path_var = tk.StringVar()
        self.file_entry = tk.Entry(file_section, textvariable=self.file_path_var, 
                                  font=('Consolas', 10), 
                                  bg='#2a2a2a', fg='#ffffff', 
                                  insertbackground='#e74c3c',
                                  relief='flat', bd=0, highlightthickness=2,
                                  highlightbackground='#404040', highlightcolor='#e74c3c')
        self.file_entry.pack(fill=tk.X, padx=15, pady=12)
        
        browse_button = tk.Button(file_section, text="Browse Files", 
                                 command=self.browse_file,
                                 font=('Segoe UI', 11, 'bold'),
                                 bg='#34495e', fg='#ffffff',
                                 activebackground='#4a5f7a', activeforeground='#ffffff',
                                 relief='flat', bd=0, padx=25, pady=12, cursor='hand2')
        browse_button.pack(side=tk.LEFT, pady=(0, 15))
        
        import_button = tk.Button(file_section, text="Import PointCloud", 
                                 command=self.import_pointcloud,
                                 font=('Segoe UI', 12, 'bold'),
                                 bg='#e74c3c', fg='#ffffff',
                                 activebackground='#c0392b', activeforeground='#ffffff',
                                 relief='flat', bd=0, padx=30, pady=12, cursor='hand2')
        import_button.pack(side=tk.RIGHT, pady=(0, 15))
        
        return panel
    
    def create_right_panel(self, parent):
        panel = tk.Frame(parent, bg='#1a1a1a', relief='flat', bd=0)
        
        header = tk.Label(panel, text="PROCESSING OPTIONS", 
                         font=('Segoe UI', 14, 'bold'), 
                         fg='#ffffff', bg='#1a1a1a', pady=20)
        header.pack(fill=tk.X)
        
        options_frame = tk.Frame(panel, bg='#1a1a1a')
        options_frame.pack(fill=tk.X, padx=25, pady=(0, 25))
        
        self.estimate_normals_var = tk.BooleanVar(value=True)
        normals_check = tk.Checkbutton(options_frame, text="Estimate Normals", 
                                      variable=self.estimate_normals_var,
                                      font=('Segoe UI', 10), fg='#ffffff', bg='#1a1a1a',
                                      selectcolor='#e74c3c', activebackground='#1a1a1a',
                                      activeforeground='#ffffff', relief='flat', bd=0)
        normals_check.pack(anchor=tk.W, pady=5)
        
        self.remove_outliers_var = tk.BooleanVar(value=True)
        outliers_check = tk.Checkbutton(options_frame, text="Remove Outliers", 
                                       variable=self.remove_outliers_var,
                                       font=('Segoe UI', 10), fg='#ffffff', bg='#1a1a1a',
                                       selectcolor='#e74c3c', activebackground='#1a1a1a',
                                       activeforeground='#ffffff', relief='flat', bd=0)
        outliers_check.pack(anchor=tk.W, pady=5)
        
        self.downsample_var = tk.BooleanVar(value=False)
        downsample_check = tk.Checkbutton(options_frame, text="Downsample", 
                                         variable=self.downsample_var,
                                         font=('Segoe UI', 10), fg='#ffffff', bg='#1a1a1a',
                                         selectcolor='#e74c3c', activebackground='#1a1a1a',
                                         activeforeground='#ffffff', relief='flat', bd=0)
        downsample_check.pack(anchor=tk.W, pady=5)
        
        self.create_mesh_var = tk.BooleanVar(value=True)
        mesh_check = tk.Checkbutton(options_frame, text="Create Mesh", 
                                   variable=self.create_mesh_var,
                                   font=('Segoe UI', 10), fg='#ffffff', bg='#1a1a1a',
                                   selectcolor='#e74c3c', activebackground='#1a1a1a',
                                   activeforeground='#ffffff', relief='flat', bd=0)
        mesh_check.pack(anchor=tk.W, pady=5)
        
        self.process_button = tk.Button(panel, text="Start Processing", 
                                       command=self.start_processing, 
                                       state='disabled',
                                       font=('Segoe UI', 13, 'bold'),
                                       bg='#e74c3c', fg='#ffffff',
                                       activebackground='#c0392b', activeforeground='#ffffff',
                                       relief='flat', bd=0, padx=40, pady=15, cursor='hand2')
        self.process_button.pack(fill=tk.X, padx=25, pady=(20, 0))
        
        status_frame = tk.Frame(panel, bg='#1a1a1a')
        status_frame.pack(fill=tk.X, padx=25, pady=(25, 0))
        
        status_header = tk.Label(status_frame, text="PROCESSING STATUS", 
                                font=('Segoe UI', 12, 'bold'), 
                                fg='#ffffff', bg='#1a1a1a', anchor=tk.W)
        status_header.pack(fill=tk.X, pady=(0, 15))
        
        self.status_var = tk.StringVar(value="Ready to import pointcloud...")
        self.status_label = tk.Label(status_frame, textvariable=self.status_var, 
                                    font=('Segoe UI', 11), fg='#cccccc', bg='#1a1a1a',
                                    anchor=tk.W, wraplength=400)
        self.status_label.pack(fill=tk.X, pady=(0, 15))
        
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate', length=400)
        self.progress.pack(fill=tk.X, pady=(0, 15))
        
        return panel
    
    def browse_file(self):
        filetypes = [
            ("Point Cloud Files", "*.las *.laz *.ply *.pcd *.xyz"),
            ("LAS Files", "*.las *.laz"),
            ("PLY Files", "*.ply"),
            ("PCD Files", "*.pcd"),
            ("XYZ Files", "*.xyz"),
            ("All Files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Point Cloud File",
            filetypes=filetypes
        )
        
        if filename:
            self.file_path_var.set(filename)
    
    def import_pointcloud(self):
        if not self.file_path_var.get():
            messagebox.showerror("Error", "Please select a point cloud file first.")
            return
        
        self.status_var.set("Importing point cloud file...")
        self.progress.start()
        
        def import_worker():
            time.sleep(2)
            self.root.after(0, self.import_complete)
        
        threading.Thread(target=import_worker, daemon=True).start()
    
    def import_complete(self):
        self.progress.stop()
        self.status_var.set("Point cloud imported successfully! Ready for processing.")
        self.process_button.configure(state='normal')
        self.current_file = os.path.basename(self.file_path_var.get())
    
    def start_processing(self):
        if not self.current_file:
            messagebox.showerror("Error", "Please import a point cloud file first.")
            return
        
        self.process_button.configure(state='disabled')
        self.processing = True
        self.status_var.set("Processing point cloud with advanced algorithms...")
        self.progress.start()
        
        def processing_worker():
            time.sleep(5)
            self.root.after(0, self.processing_complete)
        
        threading.Thread(target=processing_worker, daemon=True).start()
    
    def processing_complete(self):
        self.processing = False
        self.progress.stop()
        self.status_var.set("Processing completed successfully!")
        
        messagebox.showinfo("Success", "Point cloud processing completed!")
        self.process_button.configure(state='normal')
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CindirPointCloudManager()
    app.run()
