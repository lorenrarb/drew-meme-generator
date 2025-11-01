#!/bin/bash
# Download the inswapper model during build

echo "Downloading inswapper_128.onnx model..."

# Create directory
mkdir -p models

# Download from a working public source
# Using Hugging Face public model (no auth needed for this one)
curl -L -o inswapper_128.onnx "https://huggingface.co/CountFloyd/deepfake/resolve/main/inswapper_128.onnx" || \
curl -L -o inswapper_128.onnx "https://github.com/deepinsight/insightface/releases/download/v0.7/inswapper_128.onnx" || \
wget -O inswapper_128.onnx "https://huggingface.co/CountFloyd/deepfake/resolve/main/inswapper_128.onnx" || \
echo "Failed to download model. Will try during runtime."

if [ -f "inswapper_128.onnx" ]; then
    echo "Model downloaded successfully!"
    ls -lh inswapper_128.onnx
else
    echo "Warning: Model download failed. App will attempt to download at runtime."
fi
