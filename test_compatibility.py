#!/usr/bin/env python3
"""
测试 cursor-style 插件与 Hermes Agent 2026.4.16 的兼容性
"""

import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "hermes-agent-2026.4.16"))

def test_context_engine_abc():
    """测试 ContextEngine ABC 定义"""
    print("=== 测试 ContextEngine ABC 定义 ===")
    
    try:
        from agent.context_engine import ContextEngine
        print("✅ 成功导入 Hermes Agent 的 ContextEngine")
        
        # 检查 compress 方法的签名
        import inspect
        sig = inspect.signature(ContextEngine.compress)
        params = list(sig.parameters.keys())
        print(f"ContextEngine.compress 参数: {params}")
        
        # 预期的参数
        expected_params = ['self', 'messages', 'current_tokens']
        if params == expected_params:
            print(f"✅ ContextEngine.compress 签名正确: {params}")
        else:
            print(f"⚠️  ContextEngine.compress 签名不匹配")
            print(f"   期望: {expected_params}")
            print(f"   实际: {params}")
            
    except ImportError as e:
        print(f"❌ 无法导入 ContextEngine: {e}")
        return False
    
    return True

def test_cursor_style_implementation():
    """测试 cursor-style 插件的实现"""
    print("\n=== 测试 cursor-style 插件实现 ===")
    
    try:
        # 首先确保可以导入存根
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "cursor_style/tests/stubs"))
        from context_engine import ContextEngine as StubContextEngine
        print("✅ 成功导入 cursor-style 存根 ContextEngine")
        
        # 现在测试实际的 cursor-style 引擎
        from cursor_style.engine import CursorStyleEngine
        
        # 创建实例
        engine = CursorStyleEngine()
        print(f"✅ 成功创建 CursorStyleEngine 实例: {engine.name}")
        
        # 检查是否继承自 ContextEngine
        if isinstance(engine, StubContextEngine):
            print("✅ CursorStyleEngine 是 ContextEngine 的子类")
        else:
            print("❌ CursorStyleEngine 不是 ContextEngine 的子类")
            return False
            
        # 检查 compress 方法签名
        import inspect
        sig = inspect.signature(engine.compress)
        params = list(sig.parameters.keys())
        print(f"CursorStyleEngine.compress 参数: {params}")
        
        # cursor-style 的 compress 应该有 focus_topic 参数
        expected_params = ['self', 'messages', 'current_tokens', 'focus_topic']
        if params == expected_params:
            print(f"✅ CursorStyleEngine.compress 签名正确: {params}")
        else:
            print(f"⚠️  CursorStyleEngine.compress 签名不匹配")
            print(f"   期望: {expected_params}")
            print(f"   实际: {params}")
            
        # 测试基本功能
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        
        # 测试 should_compress_preflight
        result = engine.should_compress_preflight(test_messages)
        print(f"✅ should_compress_preflight 测试通过: {result}")
        
        # 测试 update_from_response
        engine.update_from_response({"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150})
        print(f"✅ update_from_response 测试通过")
        print(f"   更新后: prompt_tokens={engine.last_prompt_tokens}, completion_tokens={engine.last_completion_tokens}")
        
        # 测试 get_status
        status = engine.get_status()
        print(f"✅ get_status 测试通过: {status}")
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_hermes_context_compressor():
    """测试 Hermes Agent 内置的 ContextCompressor"""
    print("\n=== 测试 Hermes Agent ContextCompressor ===")
    
    try:
        from agent.context_compressor import ContextCompressor
        
        # 创建实例
        compressor = ContextCompressor(
            model="gpt-4",
            context_length=128000,
            threshold_percent=0.5,
            protect_first_n=3,
            protect_last_n=6,
        )
        print(f"✅ 成功创建 ContextCompressor 实例: {compressor.name}")
        
        # 检查 compress 方法签名
        import inspect
        sig = inspect.signature(compressor.compress)
        params = list(sig.parameters.keys())
        print(f"ContextCompressor.compress 参数: {params}")
        
        # ContextCompressor 也应该有 focus_topic 参数
        expected_params = ['self', 'messages', 'current_tokens', 'focus_topic']
        if params == expected_params:
            print(f"✅ ContextCompressor.compress 签名正确: {params}")
        else:
            print(f"⚠️  ContextCompressor.compress 签名不匹配")
            print(f"   期望: {expected_params}")
            print(f"   实际: {params}")
            
    except ImportError as e:
        print(f"❌ 无法导入 ContextCompressor: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_plugin_loading():
    """测试插件加载机制"""
    print("\n=== 测试插件加载机制 ===")
    
    try:
        # 测试插件目录结构
        plugin_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cursor_style")
        if os.path.exists(plugin_dir):
            print(f"✅ cursor-style 插件目录存在: {plugin_dir}")
            
            # 检查必要的文件
            required_files = [
                "__init__.py",
                "engine.py",
                "token_counter.py",
                "summarizer.py",
                "history_file.py",
            ]
            
            for file in required_files:
                file_path = os.path.join(plugin_dir, file)
                if os.path.exists(file_path):
                    print(f"✅ 文件存在: {file}")
                else:
                    print(f"❌ 文件缺失: {file}")
                    return False
        else:
            print(f"❌ cursor-style 插件目录不存在: {plugin_dir}")
            return False
            
        # 测试插件注册函数
        if os.path.exists(os.path.join(plugin_dir, "engine.py")):
            with open(os.path.join(plugin_dir, "engine.py"), 'r') as f:
                content = f.read()
                if "def register(ctx)" in content:
                    print("✅ 找到 register(ctx) 函数")
                else:
                    print("❌ 未找到 register(ctx) 函数")
                    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """主测试函数"""
    print("开始测试 cursor-style 插件与 Hermes Agent 2026.4.16 的兼容性")
    print("=" * 60)
    
    tests = [
        ("ContextEngine ABC 定义", test_context_engine_abc),
        ("cursor-style 插件实现", test_cursor_style_implementation),
        ("Hermes ContextCompressor", test_hermes_context_compressor),
        ("插件加载机制", test_plugin_loading),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print("-" * 60)
    
    all_passed = True
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name:30} {status}")
        if not success:
            all_passed = False
    
    print("-" * 60)
    if all_passed:
        print("🎉 所有测试通过！cursor-style 插件与 Hermes Agent 2026.4.16 兼容")
    else:
        print("⚠️  部分测试失败，存在兼容性问题")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)