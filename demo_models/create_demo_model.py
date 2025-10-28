#!/usr/bin/env python3
"""
创建示例ONNX模型文件用于演示

此脚本创建虚拟的ONNX模型文件用于测试转换流程。
"""

import os
from pathlib import Path

def create_demo_model(model_type: str, output_path: str):
    """创建演示用的ONNX模型"""

    # 创建虚拟的ONNX文件内容
    # 这不是真正的ONNX格式，只是用于演示转换流程
    model_content = f"""# {model_type} 演示模型
# 这是一个虚拟的ONNX模型文件，用于演示转换流程
# 实际使用时，请使用真实的ONNX模型

Model Type: {model_type}
Input Shape: [1, 80, 100]
Output Shape: [1, 256]
Quantization: FP16
Created: {Path(__file__).stat().st_mtime}

此文件仅用于演示目的。
转换工具会识别这是一个示例文件并执行相应的处理。
"""

    # 写入文件
    with open(output_path, 'w') as f:
        f.write(model_content)

    # 获取文件大小
    file_size = Path(output_path).stat().st_size

    print(f"✅ 示例{model_type}模型已创建: {output_path}")

    # 显示模型信息
    print(f"\n📊 模型信息:")
    print(f"   类型: {model_type}")
    print(f"   输入形状: [1, 80, 100]")
    print(f"   输出形状: [1, 256]")
    print(f"   文件大小: {file_size} 字节")
    print(f"   量化: FP16")

if __name__ == '__main__':
    # 创建示例模型
    models_dir = Path(__file__).parent
    models_dir.mkdir(exist_ok=True)

    # 创建3个示例模型
    create_demo_model('VITS-Cantonese', models_dir / 'vits_cantonese_demo.onnx')
    create_demo_model('SenseVoice', models_dir / 'sensevoice_demo.onnx')
    create_demo_model('Piper VITS', models_dir / 'piper_vits_demo.onnx')

    print("\n🎉 所有示例模型创建完成!")
    print(f"\n📁 模型位置: {models_dir}")
    print("\n使用方法:")
    print(f"  python convert_model.py")
    print(f"  或")
    print(f"  python execute_conversion.py --model sensevoice --input {models_dir}/sensevoice_demo.onnx")
