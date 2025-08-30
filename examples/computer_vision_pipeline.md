# Computer Vision Pipeline - PyTorch Example

Computer vision pipeline using PyTorch with native object passing for maximum performance. Demonstrates zero-copy tensor operations, GPU acceleration, and ML framework integration.

## Dependencies

```json
{
  "requirements": [
    "torch>=1.9.0",
    "torchvision>=0.13.0",
    "Pillow>=8.0.0",
    "numpy>=1.21.0"
  ],
  "optional": [
    "cuda-toolkit>=11.0"
  ],
  "python": ">=3.8",
  "notes": "CUDA support requires compatible NVIDIA GPU and drivers. Models will download automatically on first run (~100MB for ResNet-50)."
}
```

## Node: Image Path Input (ID: image-path-input)

Provides image file path input through GUI text field for computer vision pipeline processing.

### Metadata

```json
{
  "uuid": "image-path-input",
  "title": "Image Path Input",
  "pos": [50, 200],
  "size": [280, 180],
  "colors": {
    "title": "#007bff",
    "body": "#0056b3"
  },
  "gui_state": {
    "image_path": "examples/sample_images/cat.jpg"
  }
}
```

### Logic

```python
@node_entry
def provide_image_path(image_path: str) -> str:
    print(f"Image path: {image_path}")
    return image_path
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton

layout.addWidget(QLabel('Image File Path:', parent))
widgets['image_path'] = QLineEdit(parent)
widgets['image_path'].setPlaceholderText('Path to image file (jpg, png)')
widgets['image_path'].setText('examples/sample_images/cat.jpg')
layout.addWidget(widgets['image_path'])

widgets['browse_btn'] = QPushButton('Browse...', parent)
layout.addWidget(widgets['browse_btn'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {
        'image_path': widgets['image_path'].text()
    }

def set_values(widgets, outputs):
    # Input node doesn't need to display outputs
    pass

def set_initial_state(widgets, state):
    widgets['image_path'].setText(state.get('image_path', 'examples/sample_images/cat.jpg'))
```


## Node: Image Loader (ID: image-loader)

Loads image from file path and converts to PyTorch tensor for processing pipeline.

### Metadata

```json
{
  "uuid": "image-loader",
  "title": "Image Loader",
  "pos": [400, 100],
  "size": [250, 200],
  "colors": {
    "title": "#28a745",
    "body": "#1e7e34"
  },
  "gui_state": {}
}
```

### Logic

```python
import os
from typing import Tuple, Dict, Any
from PIL import Image
import torch
import torchvision.transforms as transforms

@node_entry
def load_image(image_path: str) -> Tuple[torch.Tensor, Tuple[int, int], int]:
    # Handle relative paths by making them absolute from project root
    if not os.path.isabs(image_path):
        # Get project root directory
        import sys
        project_root = os.path.dirname(os.path.dirname(sys.modules['__main__'].__file__)) if hasattr(sys.modules['__main__'], '__file__') else os.getcwd()
        image_path = os.path.join(project_root, image_path)
    
    # Load image
    image = Image.open(image_path).convert('RGB')
    
    # Convert to tensor for pipeline
    transform = transforms.ToTensor()
    tensor = transform(image)
    
    print(f"Loaded image: {image.size} -> tensor shape: {tensor.shape}")
    print(f"Tensor device: {tensor.device}, dtype: {tensor.dtype}")
    
    return tensor, image.size, tensor.shape[0]
```


## Node: Image Preprocessor (ID: image-preprocessor)

Preprocesses image tensor for ResNet model input with standardization and resizing.

### Metadata

```json
{
  "uuid": "image-preprocessor", 
  "title": "Image Preprocessor",
  "pos": [750, 100],
  "size": [250, 200],
  "colors": {
    "title": "#fd7e14",
    "body": "#e8590c"
  },
  "gui_state": {}
}
```

### Logic

```python
from typing import Tuple, List
import torch
import torchvision.transforms as transforms

@node_entry
def preprocess_image(image_tensor: torch.Tensor) -> Tuple[torch.Tensor, List[int], str]:
    # Define preprocessing pipeline for ImageNet models
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    
    # Apply preprocessing and add batch dimension
    processed_tensor = preprocess(image_tensor).unsqueeze(0)
    
    print(f"Preprocessed tensor shape: {processed_tensor.shape}")
    print(f"Tensor range: [{processed_tensor.min():.3f}, {processed_tensor.max():.3f}]")
    
    return processed_tensor, list(processed_tensor.shape), str(processed_tensor.device)
```


## Node: Feature Extractor (ID: feature-extractor)

Extracts features using pre-trained ResNet-50 backbone with GPU acceleration.

### Metadata

```json
{
  "uuid": "feature-extractor",
  "title": "Feature Extractor",
  "pos": [1100, 100], 
  "size": [250, 200],
  "colors": {
    "title": "#6f42c1",
    "body": "#563d7c"
  },
  "gui_state": {}
}
```

### Logic

```python
from typing import Tuple
import torch
import torchvision.models as models

@node_entry
def extract_features(preprocessed_tensor: torch.Tensor) -> Tuple[torch.Tensor, int, str]:
    # Load pre-trained ResNet (cached after first load)
    if not hasattr(extract_features, 'model'):
        print("Loading ResNet-50 model...")
        extract_features.model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        extract_features.model.eval()
        
        # Move to GPU if available
        if torch.cuda.is_available():
            extract_features.model = extract_features.model.cuda()
            print("Model moved to GPU")
    
    tensor = preprocessed_tensor
    
    # Move tensor to same device as model
    if torch.cuda.is_available():
        tensor = tensor.cuda()
    
    # Extract features (no gradients needed)
    with torch.no_grad():
        # Remove final classification layer to get features
        features = torch.nn.Sequential(*list(extract_features.model.children())[:-1])
        feature_vector = features(tensor)
        feature_vector = feature_vector.squeeze()  # Remove batch/spatial dims
    
    print(f"Extracted features shape: {feature_vector.shape}")
    print(f"Feature vector device: {feature_vector.device}")
    
    return feature_vector, feature_vector.shape[0], str(feature_vector.device)
```


## Node: Classifier (ID: classifier)

Performs image classification using ResNet-50 with top-5 predictions.

### Metadata

```json
{
  "uuid": "classifier",
  "title": "Classifier",
  "pos": [750, 350],
  "size": [250, 200],
  "colors": {
    "title": "#dc3545",
    "body": "#bd2130"
  },
  "gui_state": {}
}
```

### Logic

```python
from typing import Tuple, Dict
import torch
import torchvision.models as models

@node_entry 
def classify_image(preprocessed_tensor: torch.Tensor) -> Tuple[Dict[str, float], str, float]:
    # Load full ResNet model for classification
    if not hasattr(classify_image, 'model'):
        print("Loading ResNet-50 classifier...")
        classify_image.model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        classify_image.model.eval()
        
        if torch.cuda.is_available():
            classify_image.model = classify_image.model.cuda()
    
    tensor = preprocessed_tensor
    
    # Move tensor to same device as model
    if torch.cuda.is_available():
        tensor = tensor.cuda()
    
    # Get classification scores
    with torch.no_grad():
        logits = classify_image.model(tensor)
        probabilities = torch.softmax(logits, dim=1)
    
    # Get top 5 predictions
    top5_probs, top5_indices = torch.topk(probabilities, 5, dim=1)
    
    # Convert to CPU for final processing
    top5_probs = top5_probs.cpu().squeeze()
    top5_indices = top5_indices.cpu().squeeze()
    
    # Create simplified class labels (in real use, load from ImageNet labels)
    predictions = {}
    class_names = [
        "tabby_cat", "egyptian_cat", "persian_cat", "tiger_cat", "siamese_cat",
        "golden_retriever", "labrador", "german_shepherd", "poodle", "beagle"
    ]
    
    for i in range(5):
        class_idx = top5_indices[i].item()
        confidence = top5_probs[i].item()
        # Use simplified names or generic class names
        if class_idx < len(class_names):
            class_name = class_names[class_idx]
        else:
            class_name = f"class_{class_idx}"
        predictions[class_name] = confidence
    
    top_class = max(predictions, key=predictions.get)
    top_confidence = max(predictions.values())
    
    print(f"Top prediction: {top_class} ({top_confidence:.4f})")
    print(f"Top 5 predictions: {predictions}")
    
    return predictions, top_class, top_confidence
```


## Node: Results Display (ID: results-display)

Displays classification results with metadata and performance information.

### Metadata

```json
{
  "uuid": "results-display",
  "title": "Results Display", 
  "pos": [400, 450],
  "size": [300, 350],
  "colors": {
    "title": "#17a2b8",
    "body": "#117a8b"
  },
  "gui_state": {}
}
```

### Logic

```python
from typing import Tuple, Dict, Any
import torch

@node_entry
def display_results(
    predictions: Dict[str, float],
    top_class: str, 
    top_confidence: float,
    original_size: Tuple[int, int],
    channels: int,
    device_info: str
) -> Dict[str, Any]:
    
    # Format comprehensive results
    results = {
        "classification": {
            "predicted_class": top_class,
            "confidence": f"{top_confidence:.4f}",
            "top_5_predictions": predictions
        },
        "image_metadata": {
            "original_size": f"{original_size[0]}x{original_size[1]}",
            "channels": channels,
            "processed_device": device_info
        },
        "performance": {
            "gpu_available": torch.cuda.is_available(),
            "gpu_memory_cached": f"{torch.cuda.memory_cached() / 1024**2:.1f}MB" if torch.cuda.is_available() else "N/A",
            "native_object_passing": "Enabled"
        }
    }
    
    # Print formatted results
    print("\n" + "="*50)
    print("COMPUTER VISION PIPELINE RESULTS")
    print("="*50)
    print(f"Predicted Class: {top_class}")
    print(f"Confidence: {top_confidence:.4f}")
    print(f"Image Size: {original_size[0]}x{original_size[1]} pixels")
    print(f"Processing Device: {device_info}")
    print(f"GPU Available: {torch.cuda.is_available()}")
    print("="*50)
    
    return results
```

### GUI Definition

```python
from PySide6.QtWidgets import QLabel, QTextEdit, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

title_label = QLabel('Computer Vision Results', parent)
title_font = QFont()
title_font.setPointSize(12)
title_font.setBold(True)
title_label.setFont(title_font)
layout.addWidget(title_label)

widgets['results_display'] = QTextEdit(parent)
widgets['results_display'].setMinimumHeight(180)
widgets['results_display'].setReadOnly(True)
widgets['results_display'].setPlainText('Run pipeline to see results...')
font = QFont('Courier New', 9)
widgets['results_display'].setFont(font)
layout.addWidget(widgets['results_display'])

widgets['clear_btn'] = QPushButton('Clear Results', parent)
layout.addWidget(widgets['clear_btn'])
```

### GUI State Handler

```python
def get_values(widgets):
    return {}

def set_values(widgets, outputs):
    results = outputs.get('output_1', {})
    
    if results:
        # Format results for display
        display_text = ""
        
        if 'classification' in results:
            cls_data = results['classification']
            display_text += f"Predicted: {cls_data.get('predicted_class', 'Unknown')}\n"
            display_text += f"Confidence: {cls_data.get('confidence', 'N/A')}\n\n"
            
            if 'top_5_predictions' in cls_data:
                display_text += "Top 5 Predictions:\n"
                for cls_name, conf in cls_data['top_5_predictions'].items():
                    display_text += f"  {cls_name}: {conf:.4f}\n"
                display_text += "\n"
        
        if 'image_metadata' in results:
            meta = results['image_metadata']
            display_text += f"Image Size: {meta.get('original_size', 'Unknown')}\n"
            display_text += f"Channels: {meta.get('channels', 'Unknown')}\n"
            display_text += f"Device: {meta.get('processed_device', 'Unknown')}\n\n"
        
        if 'performance' in results:
            perf = results['performance']
            display_text += f"GPU Available: {perf.get('gpu_available', 'Unknown')}\n"
            display_text += f"GPU Memory: {perf.get('gpu_memory_cached', 'N/A')}\n"
            display_text += f"Native Object Passing: {perf.get('native_object_passing', 'Unknown')}"
        
        widgets['results_display'].setPlainText(display_text)

def set_initial_state(widgets, state):
    pass
```


## Connections

```json
[
  {
    "start_node_uuid": "image-path-input",
    "start_pin_name": "exec_out",
    "end_node_uuid": "image-loader",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "image-path-input",
    "start_pin_name": "output_1",
    "end_node_uuid": "image-loader", 
    "end_pin_name": "image_path"
  },
  {
    "start_node_uuid": "image-loader",
    "start_pin_name": "exec_out",
    "end_node_uuid": "image-preprocessor",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "image-loader",
    "start_pin_name": "output_1",
    "end_node_uuid": "image-preprocessor",
    "end_pin_name": "image_tensor"
  },
  {
    "start_node_uuid": "image-preprocessor",
    "start_pin_name": "exec_out", 
    "end_node_uuid": "feature-extractor",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "image-preprocessor",
    "start_pin_name": "output_1",
    "end_node_uuid": "feature-extractor",
    "end_pin_name": "preprocessed_tensor"
  },
  {
    "start_node_uuid": "image-preprocessor",
    "start_pin_name": "output_1",
    "end_node_uuid": "classifier",
    "end_pin_name": "preprocessed_tensor"
  },
  {
    "start_node_uuid": "feature-extractor",
    "start_pin_name": "exec_out",
    "end_node_uuid": "classifier",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "classifier",
    "start_pin_name": "exec_out",
    "end_node_uuid": "results-display",
    "end_pin_name": "exec_in"
  },
  {
    "start_node_uuid": "classifier",
    "start_pin_name": "output_1",
    "end_node_uuid": "results-display",
    "end_pin_name": "predictions"
  },
  {
    "start_node_uuid": "classifier",
    "start_pin_name": "output_2",
    "end_node_uuid": "results-display",
    "end_pin_name": "top_class"
  },
  {
    "start_node_uuid": "classifier",
    "start_pin_name": "output_3",
    "end_node_uuid": "results-display",
    "end_pin_name": "top_confidence"
  },
  {
    "start_node_uuid": "image-loader",
    "start_pin_name": "output_2",
    "end_node_uuid": "results-display",
    "end_pin_name": "original_size"
  },
  {
    "start_node_uuid": "image-loader", 
    "start_pin_name": "output_3",
    "end_node_uuid": "results-display",
    "end_pin_name": "channels"
  },
  {
    "start_node_uuid": "image-preprocessor",
    "start_pin_name": "output_3",
    "end_node_uuid": "results-display",
    "end_pin_name": "device_info"
  }
]
```