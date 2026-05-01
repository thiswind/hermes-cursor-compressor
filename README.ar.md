# محرك ضغط السياق بأسلوب Cursor لـ Hermes Agent

**[English](README.md)** | **[中文](README.zh-CN.md)** | **[العربية](README.ar.md)**

إضافة قابلة للتوصيل تستبدل ضاغط السياق المدمج في Hermes Agent
بنهج مستوحى من Cursor IDE.

## المشكلة التي يحلها

يحتوي ضاغط السياق المدمج في Hermes Agent على خطأ حرج: يحتفظ بشكل دائم
بأول 3 رسائل (مطالبة النظام + أول تبادل بين المستخدم والمساعد).
عندما يزداد طول المشروع ويتم تشغيل الضغط، يرى النموذج الطلب الأصلي
في أعلى السياق و**يعود إلى الموضوع الأول**، مما يجعل المشاريع الطويلة
مستحيلة الإنجاز.

## كيف يعمل

مستوحى من إدارة السياق في Cursor IDE:

1. **بدون تثبيت المحادثة الأولية** — يتم حماية مطالبة النظام فقط.
   جميع رسائل المستخدم/المساعد يتم ضغطها بالتساوي. هذا هو الإصلاح الأساسي.

2. **مطالبة تلخيص بسيطة** — يستخدم نهج Cursor: "يرجى تلخيص المحادثة"
   بدلاً من القالب المُهيكل المكون من 11 قسماً في Hermes والذي يُفسر
   أحياناً بشكل خاطئ على أنه تعليمات.

3. **ذاكرة ثنائية المستوى** — قبل الضغط، تُحفظ المحادثة الكاملة
   في ملف JSONL. يتضمن الملخص مرجعاً لهذا الملف حتى يتمكن الوكيل
   من البحث فيه لاسترجاع التفاصيل المفقودة.

4. **حساب دقيق للرموز** — يستخدم `tiktoken` (cl100k_base) لتقدير
   دقيق ومتعدد اللغات للرموز. يُصلح خطأ `len(text)//4` الذي يُقلل
   بشكل كبير من تقدير الرموز للغات CJK.

5. **تقليم مخرجات الأدوات** — تُستبدل مخرجات الأدوات القديمة
   بملخصات من سطر واحد قبل تلخيص LLM، مما يقلل الضوضاء والتكلفة.

## المتطلبات المسبقة

- Python 3.9+
- [Hermes Agent](https://github.com/NousResearch/hermes-agent/) مثبت
  (الموقع الافتراضي: `~/.hermes`)
- `tiktoken` (مطلوب لحساب دقيق للرموز):

```bash
pip install tiktoken
```

## التثبيت

### التثبيت التلقائي (موصى به)

```bash
# تشغيل سكريبت التثبيت مباشرة
python <(curl -fsSL https://raw.githubusercontent.com/thiswind/hermes-cursor-compressor/main/install.py)

# أو إذا قمت باستنساخ المستودع مسبقاً
python install.py
```

سيقوم السكريبت بـ:
1. تثبيت ملفات الإضافة في الموقع الصحيح
2. تثبيت تبعية tiktoken
3. تحديث `config.yaml` تلقائياً
4. إعادة تشغيل بوابة Hermes Agent

### التثبيت اليدوي

```bash
# 1. استنساخ المستودع
git clone https://github.com/thiswind/hermes-cursor-compressor.git

# 2. نسخ ملفات الإضافة إلى الموقع الصحيح (مهم: الدليل الفرعي hermes-agent)
cp -r hermes-cursor-compressor/cursor_style/ ~/.hermes/hermes-agent/plugins/context_engine/cursor_style/

# 3. تثبيت tiktoken
pip install tiktoken

# 4. في ~/.hermes/config.yaml أضف:
#    context:
#      engine: "cursor_style"

# 5. أعد تشغيل Hermes Agent
hermes gateway restart
```

### التحقق من التثبيت

بعد التثبيت، تحقق من تحميل المحرك بشكل صحيح:

```bash
cd ~/.hermes/hermes-agent
python -c "
from plugins.context_engine import discover_context_engines, load_context_engine
print('المحركات المتاحة:')
for name, desc, avail in discover_context_engines():
    print(f'  - {name}: {\"✅ متاح\" if avail else \"❌ غير متاح\"}')

engine = load_context_engine('cursor_style')
if engine:
    print('\\n✅ تم تحميل محرك cursor_style بنجاح!')
else:
    print('\\n❌ فشل تحميل محرك cursor_style')
"
```

يجب أن ترى:
```
المحركات المتاحة:
  - cursor_style: ✅ متاح

✅ تم تحميل محرك cursor_style بنجاح!
```

## إلغاء التثبيت

### إلغاء التثبيت التلقائي (موصى به)

```bash
# تشغيل سكريبت الإلغاء مباشرة
python <(curl -fsSL https://raw.githubusercontent.com/thiswind/hermes-cursor-compressor/main/uninstall.py)

# أو إذا قمت باستنساخ المستودع مسبقاً
python uninstall.py
```

### إلغاء التثبيت اليدوي

```bash
rm -rf ~/.hermes/hermes-agent/plugins/context_engine/cursor_style
# ثم احذف "context.engine: cursor_style" من ~/.hermes/config.yaml
# أعد تشغيل Hermes Agent
```

### اختياري: تجاوز نموذج التلخيص

بشكل افتراضي، يستخدم المحرك نموذج الضغط المساعد في Hermes Agent
(مثل Gemini Flash). لتجاوز ذلك، قم بالتكوين عبر `auxiliary.compression`:

```yaml
auxiliary:
  compression:
    model: "gemini-2.5-flash"
    provider: "auto"
    timeout: 30
```

## هيكل المشروع

```
cursor_style/
├── __init__.py          # تهيئة الحزمة + تصدير دالة register
├── plugin.yaml          # بيانات الإضافة الوصفية
├── engine.py            # CursorStyleEngine (تطبيق ContextEngine ABC)
├── token_counter.py     # حساب دقيق متعدد اللغات للرموز (tiktoken)
├── summarizer.py        # تلخيص بسيط بأسلوب Cursor
├── history_file.py      # ذاكرة ثنائية المستوى (ملفات JSONL)
└── tests/
    ├── conftest.py      # أدوات اختبار مشتركة
    ├── stubs/           # كعب ContextEngine ABC (للاختبارات الوحدوية)
    ├── unit/            # اختبارات وحدوية (بدون Hermes Agent)
    └── integration/     # اختبارات تكامل (تتطلب Hermes Agent)
```

## تشغيل الاختبارات

```bash
# اختبارات وحدوية فقط (بدون Hermes Agent)
cd hermes-cursor-compressor
PYTHONPATH=. python -m pytest cursor_style/tests/unit/ -v

# جميع الاختبارات (بما فيها اختبارات التكامل)
PYTHONPATH=.:/path/to/hermes-agent python -m pytest cursor_style/tests/ -v
```

## مقارنة مع ضاغط السياق المدمج في Hermes

| الميزة | Hermes المدمج | أسلوب Cursor |
|--------|-------------|-------------|
| الرسائل المحمية | 3 (مطالبة النظام + المحادثة الأولية) | 1 (مطالبة النظام فقط) |
| خطأ انحراف الموضوع | نعم — الطلب الأولي دائماً مرئي | مُصلح — جميع الرسائل تُضغط بالتساوي |
| مطالبة التلخيص | قالب مُهيكل من 11 قسماً | بسيط (~1000 رمز) |
| تقدير الرموز | `len(text)//4` (غير دقيق لـ CJK) | tiktoken cl100k_base |
| ملف التاريخ | لا | نعم (JSONL، قابل للبحث) |
| مخرجات التلخيص | ~5000 رمز | ~1000 رمز |
| عتبة التشغيل | 50% من السياق | 50% من السياق |

## استكشاف الأخطاء وإصلاحها

### فشل تحميل المحرك

إذا فشل تحميل المحرك بعد التثبيت:

1. تأكد من وجود الملفات في الموقع الصحيح:
   ```bash
   ls -la ~/.hermes/hermes-agent/plugins/context_engine/cursor_style/
   ```

2. تأكد من أن `__init__.py` يصدّر دالة `register`

3. أعد تشغيل بوابة Hermes:
   ```bash
   hermes gateway restart
   ```

4. تحقق من السجلات:
   ```bash
   hermes logs --level ERROR
   ```

### مشاكل في التكوين

إذا رأيت مفاتيح `engine` مكررة في `config.yaml`:

```yaml
# ❌ خطأ (مفاتيح مكررة)
context:
  engine: "cursor_style"
  engine: compressor

# ✅ صحيح
context:
  engine: "cursor_style"
```

تم إصلاح هذه المشكلة في أحدث نسخة من `install.py`.

## الترخيص

MIT
