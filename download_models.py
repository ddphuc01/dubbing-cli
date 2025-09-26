#!/usr/bin/env python3
"""
Model download script for Video-CLI
Downloads required models for ASR functionality based on Linly-Dubbing implementation
"""

import os
import sys
from pathlib import Path
from loguru import logger

def download_funasr_models():
    """
    Download FunASR models to local directory following Linly-Dubbing structure
    """
    logger.info("Downloading FunASR models...")
    
    try:
        from modelscope.hub.snapshot_download import snapshot_download
    except ImportError:
        logger.error("ModelScope not installed. Please install it with: pip install modelscope")
        return False
    
    # Create models directory if it doesn't exist
    models_dir = Path("models/ASR/FunASR")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Define model IDs and local directories
    models_to_download = {
        "iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch": 
            "speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
        "iic/speech_fsmn_vad_zh-cn-16k-common-pytorch": 
            "speech_fsmn_vad_zh-cn-16k-common-pytorch",
        "iic/punc_ct-transformer_cn-en-common-vocab471067-large": 
            "punc_ct-transformer_cn-en-common-vocab471067-large",
        "iic/speech_campplus_sv_zh-cn_16k-common": 
            "speech_campplus_sv_zh-cn_16k-common"
    }
    
    for model_id, local_dir in models_to_download.items():
        try:
            logger.info(f"Downloading {model_id} to {local_dir}")
            model_dir = models_dir / local_dir
            if model_dir.exists():
                logger.info(f"Model {local_dir} already exists, skipping download")
                continue
            
            snapshot_download(
                model_id=model_id,
                local_dir=str(model_dir),
                local_dir_use_symlinks=False
            )
            logger.success(f"Successfully downloaded {local_dir}")
        except Exception as e:
            logger.error(f"Failed to download {model_id}: {str(e)}")
            return False
    
    logger.success("All FunASR models downloaded successfully!")
    return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Download models for Video-CLI ASR functionality")
    parser.add_argument("--model-type", choices=["funasr"], default="funasr", 
                        help="Type of models to download")
    
    args = parser.parse_args()
    
    if args.model_type == "funasr":
        success = download_funasr_models()
    else:
        logger.error(f"Unknown model type: {args.model_type}")
        sys.exit(1)
    
    if success:
        logger.success("Model download completed successfully!")
    else:
        logger.error("Model download failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
