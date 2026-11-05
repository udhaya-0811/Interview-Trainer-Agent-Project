# AI/ML Engineer Interview Knowledge Base
# Role: AI/ML Engineer | Category: Technical

---
## Q1 | difficulty: beginner
**Question:** What is the difference between supervised, unsupervised, and reinforcement learning?

**Answer:**
- **Supervised learning:** model learns from labelled data (input-output pairs). Examples: classification (spam detection), regression (house price prediction). Algorithms: Linear Regression, SVM, Random Forest, Neural Networks.
- **Unsupervised learning:** model finds patterns in unlabelled data. Examples: clustering (customer segmentation), dimensionality reduction (PCA). Algorithms: K-Means, DBSCAN, Autoencoders.
- **Reinforcement learning:** agent learns by interacting with an environment, receiving rewards/penalties. Examples: game playing (AlphaGo), robotics. Key concepts: policy, reward, state, action, Q-learning, PPO.
- **Semi-supervised** combines a small amount of labelled data with large unlabelled data.

---
## Q2 | difficulty: beginner
**Question:** What is the bias-variance tradeoff?

**Answer:**
- **Bias:** error from incorrect assumptions in the model. High bias → underfitting (model too simple).
- **Variance:** error from sensitivity to fluctuations in training data. High variance → overfitting (model too complex).
- **Tradeoff:** as model complexity increases, bias decreases but variance increases. Optimal model minimises total error (bias² + variance + irreducible noise).
- Solutions for overfitting: regularisation (L1/L2), dropout, early stopping, cross-validation, more data.
- Solutions for underfitting: increase model complexity, add features, reduce regularisation.

---
## Q3 | difficulty: intermediate
**Question:** Explain gradient descent and its variants (SGD, Mini-batch, Adam).

**Answer:**
**Gradient descent** minimises the loss function by iteratively updating parameters in the negative gradient direction: θ = θ - α∇L(θ).
- **Batch GD:** uses all training examples per update. Stable but slow for large datasets.
- **SGD (Stochastic):** one example per update. Fast but noisy; can escape local minima.
- **Mini-batch GD:** compromise – uses a small batch (32-256). Most common in practice.
- **Adam (Adaptive Moment Estimation):** combines momentum (moving avg of gradients) with RMSProp (moving avg of squared gradients). Adapts learning rate per parameter. Default choice for deep learning.
- Learning rate scheduling: reduce on plateau, cosine annealing, warmup.

---
## Q4 | difficulty: intermediate
**Question:** What is regularisation in machine learning? L1 vs L2?

**Answer:**
Regularisation adds a penalty term to the loss function to prevent overfitting.
- **L1 (Lasso):** penalty = λΣ|wᵢ|. Induces sparsity (drives some weights to exactly zero), useful for feature selection.
- **L2 (Ridge):** penalty = λΣwᵢ². Shrinks all weights but rarely to zero. Better when all features contribute.
- **Elastic Net:** combines L1 and L2.
- **Dropout:** randomly zeroes neurons during training (NN-specific regularisation).
- **Early stopping:** stop training when validation loss starts increasing.

---
## Q5 | difficulty: intermediate
**Question:** What is cross-validation and why is it important?

**Answer:**
Cross-validation estimates model performance on unseen data without a separate test set.
**k-fold CV:** split data into k folds; train on k-1, validate on 1; rotate; average scores.
Benefits: more reliable performance estimate (reduces variance compared to single train/test split), uses all data for both training and validation.
**Stratified k-fold:** preserves class distribution in each fold (important for imbalanced datasets).
**LOOCV** (Leave-One-Out): extreme case of k=n; high variance, computationally expensive.
Use CV for model selection and hyperparameter tuning; keep a final holdout test set untouched.

---
## Q6 | difficulty: advanced
**Question:** Explain the Transformer architecture and self-attention mechanism.

**Answer:**
The Transformer (Vaswani et al., 2017) replaced RNNs with self-attention for parallel sequence processing.
**Self-attention:** computes attention scores between all token pairs.
- Queries (Q), Keys (K), Values (V) are linear projections of input embeddings.
- Attention(Q,K,V) = softmax(QKᵀ/√dₖ)V
- Scaled dot product prevents vanishing gradients for large dₖ.
**Multi-head attention:** runs h attention heads in parallel, concatenates, and projects. Captures different types of relationships simultaneously.
**Architecture:** Encoder (bidirectional attention) + Decoder (masked + cross-attention). BERT uses encoder only; GPT uses decoder only; T5 uses full encoder-decoder.
**Positional encoding:** adds position information (sinusoidal or learned) since attention is permutation-invariant.

---
## Q7 | difficulty: advanced
**Question:** What is fine-tuning an LLM? What are the different approaches?

**Answer:**
Fine-tuning adapts a pre-trained LLM to a specific task/domain using task-specific data.
Approaches:
- **Full fine-tuning:** update all parameters. Most effective but expensive (memory, compute).
- **LoRA (Low-Rank Adaptation):** freeze base model; inject trainable low-rank matrices into attention layers. Efficient (trains ~0.1% of params).
- **QLoRA:** LoRA with quantised base model (4-bit). Enables fine-tuning large models on consumer GPUs.
- **Prompt tuning / prefix tuning:** prepend trainable tokens to input; base model frozen.
- **RLHF (Reinforcement Learning from Human Feedback):** align model with human preferences (GPT-4, Claude).
- **DPO (Direct Preference Optimisation):** simpler alternative to RLHF without separate reward model.

---
## Q8 | difficulty: advanced
**Question:** What is RAG (Retrieval-Augmented Generation)? When to use RAG vs fine-tuning?

**Answer:**
RAG combines retrieval from an external knowledge base with LLM generation. The model is given retrieved context alongside the user query at inference time.
Components: Document store → Embeddings → Vector DB → Similarity search → Context injection → LLM generation.
**RAG vs Fine-tuning:**
| Aspect | RAG | Fine-tuning |
|---|---|---|
| Knowledge updates | Easy (update docs) | Requires retraining |
| Factual grounding | Strong (citable) | Weaker (hallucination risk) |
| Cost | Low inference overhead | High training cost |
| When to use | Dynamic knowledge, citations needed | Style/format, task-specific reasoning |
Best practice: use RAG for factual, up-to-date knowledge; fine-tune for style/format; combine both for best results.

---
## Q9 | difficulty: intermediate
**Question:** What is the difference between precision, recall, F1-score, and AUC-ROC?

**Answer:**
- **Precision** = TP / (TP + FP): of predicted positives, how many are correct? (Minimise false positives)
- **Recall** = TP / (TP + FN): of actual positives, how many did we find? (Minimise false negatives)
- **F1-score** = 2 × (Precision × Recall) / (Precision + Recall): harmonic mean; balanced metric for imbalanced datasets.
- **AUC-ROC:** area under the ROC curve (TPR vs FPR at different thresholds). AUC=1 is perfect; 0.5 is random. Threshold-independent evaluation.
Use F1 when false positives and false negatives have different costs (medical diagnosis); use AUC when comparing models across thresholds.

---
## Q10 | difficulty: intermediate
**Question:** How do you handle imbalanced datasets?

**Answer:**
Techniques:
1. **Resampling:** oversample minority (SMOTE) or undersample majority.
2. **Class weights:** assign higher loss penalty to minority class (`class_weight='balanced'` in sklearn).
3. **Threshold tuning:** adjust decision threshold based on business requirements.
4. **Ensemble methods:** BalancedBaggingClassifier, EasyEnsemble.
5. **Metrics:** use F1, AUC-ROC, precision-recall curve instead of accuracy.
6. **Data collection:** acquire more minority class samples if possible.
SMOTE generates synthetic minority samples by interpolating between nearest neighbours.

---
## Q11 | difficulty: advanced
**Question:** Explain the architecture and training process of a CNN for image classification.

**Answer:**
A CNN uses convolutional layers to extract spatial features from images.
Architecture layers:
- **Conv layer:** applies learnable filters (kernels) to detect edges, textures, patterns via dot products. Output is a feature map.
- **ReLU activation:** introduces non-linearity.
- **Pooling (MaxPool):** spatial downsampling, reduces dimensions, adds translation invariance.
- **Fully Connected (FC) layers:** classify based on extracted features.
- **Softmax output:** probability distribution over classes.
Training: backpropagation updates filter weights to minimise cross-entropy loss.
Transfer learning: use pre-trained models (ResNet, EfficientNet) as feature extractors, fine-tune top layers on new task.

---
## Q12 | difficulty: advanced
**Question:** What is MLOps? Describe an end-to-end ML pipeline.

**Answer:**
MLOps applies DevOps principles to ML: automating and monitoring the full ML lifecycle.
End-to-end pipeline:
1. **Data ingestion & versioning** (DVC, Delta Lake)
2. **Feature engineering & validation** (Great Expectations)
3. **Experiment tracking** (MLflow, W&B)
4. **Model training** (distributed: Ray, Horovod)
5. **Model evaluation & validation** (hold-out set, fairness checks)
6. **Model registry** (MLflow Model Registry)
7. **Deployment** (batch inference, REST API, streaming)
8. **Monitoring** (data drift, model drift with Evidently, Arize)
9. **Retraining triggers** (automated on drift or schedule)
Tools: Kubeflow, SageMaker Pipelines, Azure ML, Vertex AI.

---
## Q13 | difficulty: intermediate
**Question:** What are embeddings in NLP? How are word embeddings trained?

**Answer:**
Embeddings are dense vector representations of tokens in a continuous vector space where semantically similar tokens are geometrically close.
**Word2Vec** (Mikolov et al.): trains shallow neural network on text.
- CBOW: predict centre word from context.
- Skip-gram: predict context words from centre word.
- Negative sampling: efficient training by contrasting positive/negative pairs.
**GloVe:** matrix factorisation of global co-occurrence statistics.
**Contextual embeddings** (BERT, GPT): same word gets different embedding based on context. Generated by transformer hidden states.
**Sentence embeddings** (sentence-transformers): fine-tuned BERT to produce fixed-size sentence-level embeddings for semantic similarity.

---
## Q14 | difficulty: intermediate
**Question:** Explain the XGBoost algorithm and why it performs well on tabular data.

**Answer:**
XGBoost (eXtreme Gradient Boosting) is an ensemble of decision trees trained sequentially, where each tree corrects errors of the previous.
Key features:
- **Gradient boosting:** minimises loss using gradient of the loss function.
- **Regularisation:** L1/L2 on leaf weights prevents overfitting.
- **Tree pruning:** depth-first with threshold; removes splits that don't improve gain.
- **Missing value handling:** learns optimal direction for missing values.
- **Parallel & cache-efficient:** sorts data once and reuses; column-parallel tree construction.
XGBoost dominates structured/tabular data competitions (Kaggle) due to its bias-variance balance, speed, and built-in regularisation.

---
## Q15 | difficulty: beginner
**Question:** What is the difference between classification and regression?

**Answer:**
- **Classification:** predicts a discrete class label. Output is a category. Examples: spam/not spam, digit recognition. Loss: cross-entropy.
- **Regression:** predicts a continuous value. Output is a number. Examples: stock price, temperature. Loss: MSE, MAE.
- **Binary classification:** two classes. Algorithms: Logistic Regression, SVM, Decision Tree.
- **Multi-class:** more than two classes. Approaches: one-vs-rest, softmax output.
- **Multi-label:** multiple labels per instance. Each label treated as independent binary classification.

---
## Q16 | difficulty: intermediate
**Question:** How does backpropagation work in neural networks?

**Answer:**
Backpropagation computes gradients of the loss with respect to each parameter using the chain rule, enabling gradient descent updates.
Forward pass: compute activations layer by layer, calculate loss.
Backward pass:
1. Compute gradient of loss w.r.t. output layer.
2. Propagate gradients backwards layer by layer using chain rule: ∂L/∂wᵢ = ∂L/∂aₙ × ∂aₙ/∂wᵢ.
3. Accumulate gradients.
4. Update weights: w = w - α × ∂L/∂w.
Challenges: vanishing gradients (deep networks, sigmoid activations) → solved by ReLU, batch normalisation, residual connections.

---
## Q17 | difficulty: advanced
**Question:** What is the difference between BERT and GPT? When would you use each?

**Answer:**
| Feature | BERT | GPT |
|---|---|---|
| Architecture | Encoder-only (bidirectional) | Decoder-only (causal/unidirectional) |
| Pre-training | Masked LM + Next Sentence Prediction | Causal LM (next token prediction) |
| Best for | Classification, NER, QA, embeddings | Text generation, summarisation, chat |
| Fine-tuning | Add classification head, fine-tune | Prompt engineering or fine-tune |
BERT reads full context in both directions, making it better for understanding tasks. GPT generates text autoregressively, making it better for generation tasks. Use BERT for sentence classification, semantic search; use GPT for summarisation, code generation, chat.

---
## Q18 | difficulty: advanced
**Question:** What are vector databases? How do they work with LLMs?

**Answer:**
Vector databases store and retrieve high-dimensional embedding vectors efficiently using approximate nearest neighbour (ANN) algorithms.
Popular options: Pinecone, Weaviate, Qdrant, Milvus, FAISS (library), ChromaDB.
**ANN algorithms:** HNSW (Hierarchical Navigable Small World graphs), IVF (Inverted File Index), ANNOY (random projections).
Workflow with LLMs:
1. Chunk documents → embed with sentence-transformers or OpenAI embeddings.
2. Store vectors + metadata in vector DB.
3. At query time: embed query → retrieve top-k similar chunks → inject as context into LLM prompt.
4. LLM generates grounded response with citations.
Use cases: RAG, semantic search, recommendation systems, duplicate detection.

---
## Q19 | difficulty: intermediate
**Question:** What is feature engineering and what are common techniques?

**Answer:**
Feature engineering is the process of transforming raw data into informative representations for ML models.
Techniques:
- **Encoding:** One-hot encoding (categorical), Label encoding, Target encoding.
- **Scaling:** StandardScaler (z-score), MinMaxScaler; important for distance-based algorithms.
- **Binning:** discretise continuous variables into bins.
- **Interaction features:** products or ratios of existing features.
- **Temporal features:** extract hour, day, month, is_weekend from timestamps.
- **Text features:** TF-IDF, bag-of-words, embeddings.
- **Imputation:** mean/median/mode, KNN imputation, model-based imputation for missing values.
Feature importance: use tree-based feature importance, SHAP values, or permutation importance to select/prune features.

---
## Q20 | difficulty: advanced
**Question:** Explain attention mechanisms in transformers in detail.

**Answer:**
Attention allows the model to focus on relevant parts of the input when producing each output token.
**Scaled Dot-Product Attention:**
- Input X is projected into Q (queries), K (keys), V (values) via learned weight matrices.
- Similarity: score(qᵢ, kⱼ) = qᵢ · kⱼ / √dₖ (scaling prevents softmax saturation).
- Weights: αᵢⱼ = softmax(score(qᵢ, kⱼ) for all j).
- Output: zᵢ = Σⱼ αᵢⱼ vⱼ (weighted sum of values).
**Multi-head attention:** parallel attention heads capture different relationships (syntactic, semantic, coreference).
**Cross-attention** (in decoder): Q from decoder, K/V from encoder — attends to encoder representations.
**Causal/masked attention** (GPT): prevents attending to future tokens during training.

---
## Q21 | difficulty: intermediate
**Question:** What is model interpretability? SHAP vs LIME?

**Answer:**
Model interpretability explains how a model makes predictions — important for trust, debugging, and regulatory compliance.
**LIME (Local Interpretable Model-agnostic Explanations):** fits a simple interpretable model locally around a specific prediction. Perturbs input and observes predictions to approximate local decision boundary.
**SHAP (SHapley Additive exPlanations):** uses game-theory Shapley values to attribute each feature's contribution to the prediction. Globally consistent and locally accurate.
- `shap.TreeExplainer`: fast for tree models.
- `shap.DeepExplainer`: for neural networks.
- Waterfall/summary plots visualise feature importance.
SHAP is generally preferred for its theoretical guarantees; LIME for its speed and flexibility with any model.

---
## Q22 | difficulty: advanced
**Question:** How do you deploy a machine learning model to production?

**Answer:**
Deployment approaches:
1. **REST API** (FastAPI/Flask): wrap model in endpoint, containerise with Docker.
2. **Batch inference:** periodic predictions on large datasets (Spark, Ray).
3. **Streaming inference:** real-time features from Kafka, sub-second latency.
4. **Edge deployment:** ONNX/TFLite export for mobile/IoT devices.
Production concerns:
- **Latency/throughput optimisation:** model quantisation (FP16/INT8), TorchScript, ONNX export, TensorRT.
- **Scaling:** Kubernetes HPA, model servers (TorchServe, Triton Inference Server).
- **Monitoring:** data drift (Kolmogorov-Smirnov), model drift (PSI), performance degradation alerts.
- **Versioning & rollback:** shadow deployment, A/B testing, canary release.

---
## Q23 | difficulty: intermediate
**Question:** What is the curse of dimensionality?

**Answer:**
As feature dimensions increase, the data becomes increasingly sparse. Key effects:
- Distance metrics become less meaningful (all points become equidistant).
- Exponentially more data needed to maintain data density.
- Models overfit more easily.
Solutions:
- **Dimensionality reduction:** PCA (linear), t-SNE/UMAP (non-linear for visualisation), Autoencoders.
- **Feature selection:** remove irrelevant/redundant features.
- **Regularisation:** L1/L2 discourage using all features.
PCA projects data onto top principal components (directions of maximum variance) while minimising reconstruction error.

---
## Q24 | difficulty: intermediate
**Question:** What is transfer learning and when should you use it?

**Answer:**
Transfer learning reuses representations learned on a large task (source domain) for a related but different task (target domain).
Approaches:
1. **Feature extraction:** freeze pre-trained layers, train only final layers on new task.
2. **Fine-tuning:** unfreeze some/all layers and continue training with small learning rate.
3. **Zero-shot/few-shot:** use LLMs directly with prompting, no gradient updates.
When to use: limited labelled data, similar domains, expensive training from scratch.
Examples: ResNet/EfficientNet for image tasks, BERT for NLP tasks, GPT for generation.
Domain shift: if source and target domains differ greatly, full fine-tuning or domain-adaptive pre-training may be needed.

---
## Q25 | difficulty: advanced
**Question:** What is prompt engineering? What are effective prompting techniques?

**Answer:**
Prompt engineering designs inputs to LLMs to elicit desired outputs reliably.
Techniques:
- **Zero-shot:** task description + input, no examples. Relies on model's pre-training knowledge.
- **Few-shot:** include 2-5 input-output examples. Guides format and reasoning.
- **Chain-of-Thought (CoT):** prompt the model to reason step-by-step: "Let's think step by step..." Improves multi-step reasoning.
- **Self-consistency:** sample multiple CoT paths, majority vote on final answer.
- **ReAct:** interleave reasoning and actions (tool calls). Used in agents.
- **System prompts:** set model persona, constraints, and output format.
- **Structured output prompting:** instruct the model to respond in JSON with a defined schema.
Best practice: be explicit about format, constraints, and what "good" looks like; include negative examples.

---
## Q26 | difficulty: intermediate
**Question:** What are common evaluation metrics for NLP tasks?

**Answer:**
- **BLEU (Bilingual Evaluation Understudy):** n-gram precision for machine translation.
- **ROUGE:** recall-based metrics for summarisation (ROUGE-N: n-gram recall, ROUGE-L: longest common subsequence).
- **BERTScore:** contextual similarity using BERT embeddings; better than n-gram metrics for semantic similarity.
- **Perplexity:** measures how well LM predicts text; lower is better. exp(-1/N × ΣlogP(wᵢ)).
- **Exact Match (EM) / F1:** for QA tasks.
- **Human evaluation:** fluency, coherence, factuality — often most reliable but expensive.
For RAG systems: faithfulness (does answer stay true to context?), answer relevance, context precision/recall.

---
## Q27 | difficulty: advanced
**Question:** Explain how you would build a production RAG system with IBM Granite.

**Answer:**
Architecture:
1. **Data pipeline:** collect documents, chunk by section (500-1000 tokens with overlap), extract metadata (source, date, category).
2. **Embeddings:** encode chunks with sentence-transformers `all-MiniLM-L6-v2` or IBM's embedding model.
3. **Vector store:** FAISS or ChromaDB; persist index to disk; support metadata filtering.
4. **Retrieval:** top-k cosine similarity search; apply metadata pre-filters; optional reranking (cross-encoder).
5. **Prompt construction:** system prompt with context injection: "Answer based only on the following context: {chunks}. If not found, say so."
6. **IBM Granite generation:** call `ibm-watsonx-ai` SDK with structured prompt; parse and validate output.
7. **Citations:** return chunk metadata (source, page, section) alongside response.
8. **Evaluation:** RAGAS metrics (faithfulness, answer relevance, context recall).
Key considerations: hallucination prevention via strict context-only instruction, source attribution, graceful fallback when retrieval fails.

---
## Q28 | difficulty: intermediate
**Question:** What is data leakage in ML and how do you prevent it?

**Answer:**
Data leakage occurs when information from the test set inadvertently influences model training, leading to overly optimistic evaluation.
Types:
- **Train-test contamination:** preprocessing (scaling, imputation) fitted on full dataset including test set.
- **Target leakage:** features contain information derived from the target (e.g., a "loan_status" feature in a default prediction model).
- **Time leakage:** using future data to predict the past in time-series models.
Prevention:
- Fit all preprocessing (scalers, encoders) only on training data; transform test data using fitted transformers.
- Use pipelines (`sklearn.pipeline.Pipeline`) to encapsulate transformers + model.
- For time-series: use `TimeSeriesSplit` instead of random splits.
- Carefully audit feature provenance.

---
## Q29 | difficulty: advanced
**Question:** What are the ethical considerations in AI/ML? What is algorithmic fairness?

**Answer:**
Key ethical concerns:
- **Bias:** models can perpetuate or amplify biases in training data (gender bias in hiring, racial bias in risk scoring).
- **Privacy:** models may memorise and reveal training data (differential privacy, federated learning).
- **Transparency:** "black box" models make it hard to audit decisions.
- **Accountability:** who is responsible for harmful model decisions?
Fairness definitions:
- **Demographic parity:** equal positive prediction rates across groups.
- **Equal opportunity:** equal true positive rates.
- **Calibration:** equal confidence of predictions across groups.
Bias mitigation: pre-processing (resampling, reweighting), in-processing (adversarial debiasing), post-processing (threshold adjustment per group). Tools: AI Fairness 360 (IBM), Fairlearn.

---
## Q30 | difficulty: advanced
**Question:** How does IBM watsonx.ai differ from other LLM platforms?

**Answer:**
IBM watsonx.ai is an enterprise AI development studio with three core components:
- **watsonx.ai:** model studio for training, fine-tuning, and inferencing foundation models including IBM Granite.
- **watsonx.data:** open, hybrid data lakehouse built on Apache Iceberg.
- **watsonx.governance:** AI lifecycle governance, bias/fairness monitoring, explainability.
Key differentiators:
- **IBM Granite models:** enterprise-focused, trained on curated data with full provenance, optimised for business tasks (code, enterprise language understanding). Indemnified for commercial use.
- **Model governance:** audit trails, model cards, risk assessment built-in.
- **Hybrid cloud:** deploy on IBM Cloud, AWS, Azure, GCP, or on-premises (via OpenShift).
- **SDK:** `ibm-watsonx-ai` Python SDK for programmatic access; supports REST API.
- **Prompt Lab:** GUI for prompt engineering and evaluation.
Lite plan provides free tier with token limits for experimentation.
