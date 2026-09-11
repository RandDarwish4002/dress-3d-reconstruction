# dress-3d-reconstruction

يحوّل هذا المشروع صورتين لقطعة ثياب (من الأمام ومن الخلف) إلى **مجسّم ثلاثي الأبعاد واحد**
مصنوع من قطعة هندسية واحدة (mesh) مع نسيج (texture) واحد مبني من الصورتين معًا.

## فكرة الأنابيب (Pipeline)

1. **إزالة الخلفية وتوحيد المقاس** — `ImagePreprocessor`
2. **بناء الهيكل الأساسي من صورة الأمام** عبر [TripoSR](https://github.com/VAST-AI-Research/TripoSR) — `TripoSRReconstructor`
3. **دمج الصورتين في نسيج واحد** بإسقاط كل صورة على الوجوه (faces) التي تقابلها في الفراغ ثلاثي الأبعاد — `TextureBaker`
4. **تصدير ملف ثلاثي الأبعاد واحد** يحمل الهيكل + النسيج المدموج — `MeshExporter`

كل هذا تديره `DressReconstructionPipeline` في خطوة واحدة.

## بنية المشروع

```
dress-3d-reconstruction/
├── requirements.txt          # مكتبات بايثون (torch يُثبَّت بشكل منفصل)
├── scripts/
│   ├── setup_env.sh           # يجهز بيئة بايثون 3.11 + PyTorch + TripoSR
│   └── run_pipeline.py        # نقطة تشغيل من سطر الأوامر
├── src/dress3d/
│   ├── config.py               # كل الإعدادات وثوابت الكاميرا في مكان واحد
│   ├── preprocessing.py        # إزالة الخلفية + توسيط الصورة
│   ├── reconstruction.py       # تشغيل TripoSR على صورة الأمام
│   ├── texture_baker.py        # دمج صورتي الأمام والخلف في نسيج واحد
│   ├── mesh_exporter.py        # تصدير الملف النهائي (.glb)
│   └── pipeline.py             # يربط كل الخطوات ببعضها
├── tests/
│   └── test_texture_baker.py   # اختبار لمنطق إسقاط الكاميرا
├── input/                      # ضع صور الأمام/الخلف هنا (غير مرفوعة لـ git)
└── output/                     # النتائج تُحفظ هنا (غير مرفوعة لـ git)
```

## الإعداد

```bash
git clone https://github.com/RandDarwish4002/dress-3d-reconstruction.git
cd dress-3d-reconstruction
bash scripts/setup_env.sh          # ينشئ /content/triposr_env ويستنسخ TripoSR
```

## التشغيل

```bash
/content/triposr_env/bin/python scripts/run_pipeline.py \
    --front input/front.jpg \
    --back input/back.jpg \
    --name my_dress
```

الناتج النهائي: `output/my_dress/my_dress.glb` — قطعة واحدة، بنسيج واحد مبني من الصورتين.

## ملاحظة أمان مهمة

تأكد أن ملف `.gitignore` يستثني أي رمز دخول (token) أو ملفات `.env`. **لا تضع توكن GitHub
مباشرة داخل كود بايثون أو دفتر Colab** — استخدم `getpass` فقط لإدخاله وقت التشغيل، ولا تطبعه أبدًا
حتى جزئيًا، ولا تُدرجه في أي ملف يُرفع إلى المستودع.
