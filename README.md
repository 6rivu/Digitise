The project digitizes handwritten mathematical documents by
generating LaTeX using deep learning models. It includes data
preprocessing, improving accuracy by fine-tuning pre-trained

SOTA models using LoRA, and developing a user-friendly interface for editing and downloading LaTeX-generated PDFs.


• High demand for this tool in tasks requiring digitization,
such as processing handwritten scientific documents.
• Research and fine-tune SOTA models, selecting the most accurate one.
• Used CV2 for word segmentation and TrOCR, Nougat/Im2Latex
for text and formula extraction.

The task is to improve model performance by changing architecture or finetuning on large dataset. I tried using SWIN V2
as encoder, and Llama 3B as decoder but encountered compu-tational limits. After preprocessing MathWriting dataset of 30k
rows to convert inkml file to images, I fine-tuned the model again, but it didn’t go good. So replaced it with the model CuiSiwei/nougat-for-formula, achieved a BLEU score of 0.81

Conclusion:
• Built end-to-end pipeline to convert Handwritten mathematical documents are converted into LaTeX
• Implemented accurate segmentation using CV2 and finetuned the models TrOCR, Im2Latex, and nougat-for-formula and achieved BELU score of 0.81 and integrated in backend

