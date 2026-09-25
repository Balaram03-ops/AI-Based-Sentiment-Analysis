# ============================================================
# AI SENTIMENT ANALYSIS
# TRAIN_MODEL.PY - VERSION 3
# ============================================================
#
# Models:
#   1. Logistic Regression
#   2. Random Forest
#
# Features:
#   - Word TF-IDF
#   - Character TF-IDF
#   - Negation-aware preprocessing
#   - 3-class sentiment classification
#   - Automatic model comparison
#   - Automatic best-model selection
#   - Holdout testing
#
# Classes:
#   Negative
#   Positive
#   Neutral
#
# ============================================================

import os
import re
import json
import warnings

import numpy as np
import pandas as pd
import joblib


from scipy.sparse import hstack
from sklearn.pipeline import FeatureUnion
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURATION
# ============================================================

DATASET_PATH = "dataset/sentiment_dataset.csv"

# Final prediction model
MODEL_PATH = "model.pkl"

# Separate Random Forest model
RANDOM_FOREST_MODEL_PATH = "random_forest_model.pkl"

# Final FeatureUnion vectorizer
VECTORIZER_PATH = "vectorizer.pkl"

# Model comparison metrics
COMPARISON_PATH = "model_comparison.json"

RANDOM_STATE = 42
 
# ============================================================
# SENTIMENT CLASSES
# ============================================================

CLASS_NAMES = [
    "Negative",
    "Neutral",
    "Positive"
]


# ============================================================
# NEGATION WORDS
# ============================================================

NEGATION_WORDS = {
    "not",
    "no",
    "never",
    "neither",
    "nor",
    "without",
    "hardly",
    "barely",
    "nothing",
    "nowhere",
    "nobody"
}


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):

    if pd.isna(text):
        return ""

    text = str(text).lower()

    # --------------------------------------------------------
    # Remove URLs
    # --------------------------------------------------------

    text = re.sub(
        r"http\S+|www\S+",
        " ",
        text
    )

    # --------------------------------------------------------
    # Remove mentions
    # --------------------------------------------------------

    text = re.sub(
        r"@\w+",
        " ",
        text
    )

    # --------------------------------------------------------
    # Remove HTML
    # --------------------------------------------------------

    text = re.sub(
        r"<.*?>",
        " ",
        text
    )

    # --------------------------------------------------------
    # Contractions
    # --------------------------------------------------------

    contractions = {

        "isn't": "is not",
        "wasn't": "was not",
        "weren't": "were not",
        "aren't": "are not",

        "don't": "do not",
        "doesn't": "does not",
        "didn't": "did not",

        "can't": "can not",
        "cannot": "can not",
        "couldn't": "could not",

        "wouldn't": "would not",
        "shouldn't": "should not",

        "won't": "will not",

        "i'm": "i am",
        "i've": "i have",
        "i'll": "i will",

        "it's": "it is",
        "that's": "that is",

        "they're": "they are",
        "we're": "we are",
        "you're": "you are"
    }

    for contraction, replacement in contractions.items():

        text = text.replace(
            contraction,
            replacement
        )

    # --------------------------------------------------------
    # Remove special characters
    # --------------------------------------------------------

    text = re.sub(
        r"[^a-z\s]",
        " ",
        text
    )

    # --------------------------------------------------------
    # Normalize spaces
    # --------------------------------------------------------

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    if not text:
        return ""

    words = text.split()

    # --------------------------------------------------------
    # NEGATION-AWARE FEATURES
    #
    # Example:
    #
    # "not good"
    #
    # becomes:
    #
    # "not good not_good"
    #
    # "never recommend"
    #
    # becomes:
    #
    # "never recommend never_recommend"
    # --------------------------------------------------------

    enhanced_words = []

    for i, word in enumerate(words):

        enhanced_words.append(word)

        if word in NEGATION_WORDS:

            # Add next 1 word
            if i + 1 < len(words):

                phrase = (
                    word
                    + "_"
                    + words[i + 1]
                )

                enhanced_words.append(
                    phrase
                )

            # Add next 2 words
            if i + 2 < len(words):

                phrase = (
                    word
                    + "_"
                    + words[i + 1]
                    + "_"
                    + words[i + 2]
                )

                enhanced_words.append(
                    phrase
                )

            # Add next 3 words
            if i + 3 < len(words):

                phrase = (
                    word
                    + "_"
                    + words[i + 1]
                    + "_"
                    + words[i + 2]
                    + "_"
                    + words[i + 3]
                )

                enhanced_words.append(
                    phrase
                )

    return " ".join(enhanced_words)


# ============================================================
# POSITIVE TRAINING SENTENCES
# ============================================================

POSITIVE_SENTENCES = [

    "I love this product",
    "I absolutely love this product",
    "This product is excellent",
    "This product is amazing",
    "This is a wonderful product",
    "The product quality is excellent",
    "The service was excellent",
    "The service was fantastic",
    "I am very happy with this product",
    "I am extremely satisfied",
    "I am satisfied with my purchase",
    "The experience was great",
    "The experience was wonderful",
    "The product works perfectly",
    "Everything works perfectly",
    "The product exceeded my expectations",
    "I highly recommend this product",
    "I would definitely recommend this product",
    "This is one of the best products",
    "The quality is outstanding",
    "The customer service was excellent",
    "The staff was very helpful",
    "The delivery was fast",
    "The product arrived on time",
    "I am impressed with the quality",
    "This product is worth the money",
    "I really enjoyed this product",
    "This was a great experience",
    "The service was quick and efficient",
    "The product is reliable",
    "I am pleased with the purchase",
    "This product is fantastic",
    "I am delighted with the result",
    "The quality is superb",
    "The product is very useful",
    "The service exceeded my expectations",
    "I am happy with the result",
    "This was an excellent experience",
    "I would buy this again",
    "I will definitely purchase again",
    "The product performs very well",
    "The support team was helpful",
    "The staff were friendly",
    "The experience was enjoyable",
    "I am impressed",
    "This is a great product",
    "The product is wonderful",
    "The service is outstanding",
    "Everything was perfect",

    # Additional positive examples
    "I really like this product",
    "This is a fantastic service",
    "The product quality is very good",
    "I am pleased with the service",
    "The customer support was excellent",
    "I had a great experience",
    "The product is reliable and useful",
    "The service was smooth",
    "I am completely satisfied",
    "This product made me happy",
    "I enjoyed using this product",
    "The product is impressive",
    "The service was professional",
    "The staff were excellent",
    "I would recommend this service",
    "This purchase was excellent",
    "I am very pleased",
    "The result was excellent",
    "The product is fantastic",
    "I love the quality"
]


# ============================================================
# NEGATIVE TRAINING SENTENCES
# ============================================================

NEGATIVE_SENTENCES = [

    "I hate this product",
    "I absolutely hate this product",
    "This product is terrible",
    "This product is horrible",
    "This is a terrible product",
    "This is a horrible experience",
    "The product quality is terrible",
    "The product quality is extremely poor",
    "The service was terrible",
    "The service was awful",
    "The customer service was terrible",
    "The customer service was horrible",
    "I am very disappointed",
    "I am extremely disappointed",
    "I am unhappy with this product",
    "I am not satisfied with this product",
    "I am very dissatisfied",
    "I regret buying this product",
    "I regret spending money on this product",
    "This product is completely useless",
    "This product does not work",
    "The product does not work properly",
    "The product stopped working",
    "The product broke immediately",
    "I received a damaged product",
    "The product was defective",
    "The product is extremely poor",
    "The quality is disappointing",
    "The experience was disappointing",
    "The experience was horrible",
    "The experience was awful",
    "The service was very slow",
    "The service was frustrating",
    "The service was extremely poor",
    "The delivery was very late",
    "The product arrived damaged",
    "I had a very bad experience",
    "This was a bad experience",
    "I would never recommend this product",
    "I will never buy this product again",
    "I would not recommend this product",
    "I do not like this product",
    "I don't like this product",
    "This product is not good",
    "This product is very bad",
    "The product is bad",
    "The service is bad",
    "The service was unacceptable",
    "The quality is unacceptable",
    "The product failed completely",
    "The product failed to work",
    "I am disappointed with my purchase",
    "I am unhappy with my purchase",
    "The product is a waste of money",
    "This was a waste of money",
    "I wasted my money on this product",
    "The product is frustrating",
    "The experience was frustrating",
    "The support was unhelpful",
    "The staff was rude",
    "The staff were unhelpful",
    "The response was very poor",
    "The product did not meet my expectations",
    "This product failed my expectations",
    "I expected better but this product failed",
    "The service failed completely",
    "Nothing about this product is good",
    "There is nothing good about this product",
    "I strongly dislike this product",
    "I dislike this product",
    "This product is disappointing",
    "The result was disappointing",
    "The quality was awful",
    "The product was awful",
    "The service was awful",
    "The experience was extremely bad",
    "This product is not worth the money",

    # Additional negative examples
    "I really dislike this product",
    "This service is extremely poor",
    "The product quality is awful",
    "I am unhappy with the result",
    "The customer support was terrible",
    "I had a bad experience",
    "The product is unreliable",
    "The service was frustrating",
    "I am completely dissatisfied",
    "This product made me angry",
    "I regret purchasing this product",
    "The product is disappointing",
    "The service was unprofessional",
    "The staff were rude",
    "I would not recommend this service",
    "This purchase was terrible",
    "I am very unhappy",
    "The result was terrible",
    "The product is useless",
    "I hate the quality"
]


# ============================================================
# NEUTRAL TRAINING SENTENCES
# ============================================================

NEUTRAL_SENTENCES = [

    "The meeting is scheduled for tomorrow",
    "The meeting starts at ten",
    "The store opens at nine",
    "The store closes at eight",
    "The package arrived today",
    "The package contains a phone",
    "The product has three buttons",
    "The phone has a large screen",
    "The report contains five pages",
    "The document was submitted today",
    "The class starts at ten",
    "The train arrives at five",
    "The bus leaves at six",
    "The office is located downtown",
    "The restaurant is near the railway station",
    "The product costs fifty dollars",
    "The phone was released last year",
    "The meeting lasted one hour",
    "The package weighs two kilograms",
    "The store has three floors",

    "The product is average",
    "The service is average",
    "The experience was average",
    "The product was ordinary",
    "The experience was ordinary",
    "The service was ordinary",
    "The product is okay",
    "The service is okay",
    "The experience is okay",
    "The product was fine",
    "The service was fine",
    "The experience was fine",
    "The product is acceptable",
    "The service is acceptable",
    "The experience is acceptable",
    "The product meets the basic requirements",
    "The service meets the basic requirements",
    "The product is neither good nor bad",
    "The service is neither good nor bad",
    "The experience is neither good nor bad",
    "The product is neither impressive nor disappointing",
    "The service is neither excellent nor terrible",
    "The experience is neither positive nor negative",
    "I would not say the product was good or bad",
    "I would not say the service was good or bad",
    "There was nothing particularly impressive about it",
    "The experience was nothing special",
    "It was just an average experience",
    "The product was neither excellent nor terrible",
    "The service was neither excellent nor terrible",
    "The experience was neither excellent nor terrible",
    "The product is standard",
    "The service is standard",
    "The experience is standard",
    "The product is typical",
    "The service is typical",
    "The experience is typical",

    # Additional neutral examples
    "The product is normal",
    "The service is normal",
    "The experience was normal",
    "The product is basic",
    "The service is basic",
    "The product is satisfactory",
    "The service is satisfactory",
    "The experience was satisfactory",
    "The product was as expected",
    "The service was as expected",
    "The experience was as expected",
    "The product has the standard features",
    "The service follows the standard procedure",
    "The package contains two items",
    "The phone has four cameras",
    "The report was submitted on Monday",
    "The meeting was held yesterday",
    "The store is located near the station",
    "The product weighs one kilogram",
    "The order number is listed on the receipt"
]


# ============================================================
# HOLDOUT TEST DATA
#
# IMPORTANT:
# These sentences are NOT used for training.
# ============================================================

HOLDOUT_TESTS = [

    # --------------------------------------------------------
    # POSITIVE
    # --------------------------------------------------------

    ("I really love this product", "Positive"),
    ("This product is fantastic", "Positive"),
    ("I am extremely happy with this purchase", "Positive"),
    ("The service was excellent", "Positive"),
    ("I highly recommend this product", "Positive"),
    ("This was a wonderful experience", "Positive"),
    ("The product works perfectly", "Positive"),
    ("I am very satisfied with the result", "Positive"),
    ("The quality is outstanding", "Positive"),
    ("I would definitely buy this again", "Positive"),

    # --------------------------------------------------------
    # NEGATIVE
    # --------------------------------------------------------

    ("I hate this product", "Negative"),
    ("This product is terrible", "Negative"),
    ("I am extremely disappointed with this product", "Negative"),
    ("The service was horrible", "Negative"),
    ("I would never recommend this product", "Negative"),
    ("This product does not work", "Negative"),
    ("The quality is extremely poor", "Negative"),
    ("I regret buying this product", "Negative"),
    ("This was a terrible experience", "Negative"),
    ("I will never buy this product again", "Negative"),

    # --------------------------------------------------------
    # NEUTRAL
    # --------------------------------------------------------

    ("The product is average", "Neutral"),
    ("The service is average", "Neutral"),
    ("The experience was ordinary", "Neutral"),
    ("The product is okay", "Neutral"),
    ("The service is fine", "Neutral"),
    ("The meeting is tomorrow", "Neutral"),
    ("The package arrived today", "Neutral"),
    ("The product costs fifty dollars", "Neutral"),
    ("The product is neither good nor bad", "Neutral"),
    ("The service is neither excellent nor terrible", "Neutral"),
    ("The experience is neither positive nor negative", "Neutral"),
    ("It was just an average experience", "Neutral"),
    ("The product meets the basic requirements", "Neutral"),
    ("The experience was nothing special", "Neutral"),
    ("The product is standard", "Neutral")
]


# ============================================================
# START
# ============================================================

print("\n")
print("=" * 75)
print("AI SENTIMENT ANALYSIS MODEL TRAINING - VERSION 3")
print("=" * 75)


# ============================================================
# CHECK DATASET
# ============================================================

print("\nLoading dataset...")

if not os.path.exists(DATASET_PATH):

    raise FileNotFoundError(
        f"\nDataset not found:\n{DATASET_PATH}"
    )


df = pd.read_csv(
    DATASET_PATH,
    encoding="utf-8",
    low_memory=False
)


print(
    "Dataset loaded successfully."
)

print(
    "Dataset shape:",
    df.shape
)

print(
    "Columns:",
    list(df.columns)
)


# ============================================================
# FIND TEXT COLUMN
# ============================================================

text_candidates = [
    "tweet",
    "text",
    "sentence",
    "review",
    "content",
    "comment"
]

text_column = None

for column in text_candidates:

    if column in df.columns:

        text_column = column
        break


if text_column is None:

    object_columns = df.select_dtypes(
        include=["object"]
    ).columns

    if len(object_columns) == 0:

        raise ValueError(
            "Text column not found."
        )

    text_column = object_columns[0]


print(
    "\nText column:",
    text_column
)


# ============================================================
# FIND LABEL COLUMN
# ============================================================

label_candidates = [
    "sentiment",
    "label",
    "target",
    "class"
]

label_column = None

for column in label_candidates:

    if column in df.columns:

        label_column = column
        break


if label_column is None:

    raise ValueError(
        "Sentiment label column not found."
    )


print(
    "Label column:",
    label_column
)


# ============================================================
# CONVERT LABEL
# ============================================================

def convert_label(value):

    try:

        numeric = float(value)

        if numeric == 0:
            return "Negative"

        elif numeric == 1:
            return "Positive"

        elif numeric == 2:
            return "Neutral"

    except:

        value = str(
            value
        ).strip().lower()

        if value in [
            "negative",
            "neg"
        ]:
            return "Negative"

        if value in [
            "positive",
            "pos"
        ]:
            return "Positive"

        if value in [
            "neutral",
            "neu"
        ]:
            return "Neutral"

    return None


df["sentiment_label"] = (
    df[label_column]
    .apply(convert_label)
)


# ============================================================
# CLEAN DATASET
# ============================================================

print("\nCleaning dataset...")

df["clean_text"] = (
    df[text_column]
    .apply(clean_text)
)


before_cleaning = len(df)


df = df.dropna(
    subset=[
        "clean_text",
        "sentiment_label"
    ]
)


df = df[
    df["clean_text"].str.strip() != ""
]


df = df.drop_duplicates(
    subset=["clean_text"]
)


after_cleaning = len(df)


print(
    "Rows before cleaning:",
    before_cleaning
)

print(
    "Rows after cleaning:",
    after_cleaning
)


# ============================================================
# CLASS DISTRIBUTION
# ============================================================

print("\nOriginal class distribution:")

print(
    df["sentiment_label"]
    .value_counts()
)


# ============================================================
# BALANCED ORIGINAL DATA
# ============================================================

print(
    "\nCreating balanced original dataset..."
)


class_counts = (
    df["sentiment_label"]
    .value_counts()
)


minimum_class_count = min(

    class_counts.get(
        "Negative",
        0
    ),

    class_counts.get(
        "Positive",
        0
    ),

    class_counts.get(
        "Neutral",
        0
    )
)


# Keep training computationally manageable
samples_per_class = min(
    15000,
    minimum_class_count
)


print(
    "Samples per original class:",
    samples_per_class
)


balanced_parts = []


for sentiment in CLASS_NAMES:

    class_data = df[
        df["sentiment_label"]
        == sentiment
    ]

    sampled = class_data.sample(

        n=samples_per_class,

        random_state=RANDOM_STATE
    )

    balanced_parts.append(
        sampled
    )


balanced_df = pd.concat(
    balanced_parts,
    ignore_index=True
)


# ============================================================
# MANUAL TRAINING DATA
# ============================================================

manual_positive = pd.DataFrame({

    "clean_text": [

        clean_text(sentence)

        for sentence
        in POSITIVE_SENTENCES
    ],

    "sentiment_label":
        "Positive"
})


manual_negative = pd.DataFrame({

    "clean_text": [

        clean_text(sentence)

        for sentence
        in NEGATIVE_SENTENCES
    ],

    "sentiment_label":
        "Negative"
})


manual_neutral = pd.DataFrame({

    "clean_text": [

        clean_text(sentence)

        for sentence
        in NEUTRAL_SENTENCES
    ],

    "sentiment_label":
        "Neutral"
})


manual_df = pd.concat(

    [
        manual_positive,
        manual_negative,
        manual_neutral
    ],

    ignore_index=True
)


# ============================================================
# REMOVE HOLDOUT LEAKAGE
# ============================================================

holdout_cleaned = {

    clean_text(text)

    for text, label
    in HOLDOUT_TESTS
}


before_manual = len(
    manual_df
)


manual_df = manual_df[
    ~manual_df["clean_text"].isin(
        holdout_cleaned
    )
]


removed_manual = (
    before_manual
    - len(manual_df)
)


print(
    "\nHoldout leakage removed:",
    removed_manual
)


# ============================================================
# COMBINE DATA
# ============================================================

training_df = pd.concat(

    [
        balanced_df[
            [
                "clean_text",
                "sentiment_label"
            ]
        ],

        manual_df
    ],

    ignore_index=True
)


training_df = training_df.drop_duplicates(
    subset=["clean_text"]
)


training_df = training_df.sample(

    frac=1,

    random_state=RANDOM_STATE

).reset_index(drop=True)


print(
    "\nFinal training dataset:"
)

print(
    "Total rows:",
    len(training_df)
)

print(
    training_df[
        "sentiment_label"
    ].value_counts()
)


# ============================================================
# TRAIN / VALIDATION SPLIT
# ============================================================

X = training_df[
    "clean_text"
]

y = training_df[
    "sentiment_label"
]


X_train, X_valid, y_train, y_valid = (
    train_test_split(

        X,

        y,

        test_size=0.20,

        random_state=RANDOM_STATE,

        stratify=y
    )
)


print(
    "\nTraining samples:",
    len(X_train)
)

print(
    "Validation samples:",
    len(X_valid)
)


# ============================================================
# WORD TF-IDF
# ============================================================

print("\nCreating Word TF-IDF...")


word_vectorizer = TfidfVectorizer(

    lowercase=True,

    stop_words=None,

    ngram_range=(1, 3),

    min_df=1,

    max_df=0.98,

    max_features=60000,

    sublinear_tf=True
)


X_train_word = (
    word_vectorizer
    .fit_transform(X_train)
)


X_valid_word = (
    word_vectorizer
    .transform(X_valid)
)


print(
    "Word features:",
    X_train_word.shape
)


# ============================================================
# CHARACTER TF-IDF
# ============================================================

print(
    "\nCreating Character TF-IDF..."
)


char_vectorizer = TfidfVectorizer(

    analyzer="char_wb",

    ngram_range=(3, 5),

    min_df=2,

    max_features=25000,

    sublinear_tf=True
)


X_train_char = (
    char_vectorizer
    .fit_transform(X_train)
)


X_valid_char = (
    char_vectorizer
    .transform(X_valid)
)


print(
    "Character features:",
    X_train_char.shape
)


# ============================================================
# COMBINE FEATURES
# ============================================================

print(
    "\nCombining Word + Character features..."
)


X_train_features = hstack(

    [
        X_train_word,
        X_train_char
    ]

).tocsr()


X_valid_features = hstack(

    [
        X_valid_word,
        X_valid_char
    ]

).tocsr()


print(
    "Final training feature shape:",
    X_train_features.shape
)


# ============================================================
# MODEL 1
# LOGISTIC REGRESSION
# ============================================================

print("\n")
print("=" * 75)
print("MODEL 1 - LOGISTIC REGRESSION")
print("=" * 75)


logistic_model = LogisticRegression(

    C=1.5,

    max_iter=3000,

    class_weight="balanced",

    solver="lbfgs",

    random_state=RANDOM_STATE
)


print(
    "\nTraining Logistic Regression..."
)


logistic_model.fit(

    X_train_features,

    y_train
)


logistic_predictions = (
    logistic_model
    .predict(X_valid_features)
)


logistic_accuracy = accuracy_score(

    y_valid,

    logistic_predictions
)


logistic_precision = precision_score(

    y_valid,

    logistic_predictions,

    average="weighted",

    zero_division=0
)


logistic_recall = recall_score(

    y_valid,

    logistic_predictions,

    average="weighted",

    zero_division=0
)


logistic_f1 = f1_score(

    y_valid,

    logistic_predictions,

    average="weighted",

    zero_division=0
)


print(
    f"\nAccuracy  : {logistic_accuracy:.4f}"
)

print(
    f"Precision : {logistic_precision:.4f}"
)

print(
    f"Recall    : {logistic_recall:.4f}"
)

print(
    f"F1 Score  : {logistic_f1:.4f}"
)


print(
    "\nClassification Report:"
)


print(
    classification_report(

        y_valid,

        logistic_predictions,

        labels=CLASS_NAMES,

        zero_division=0
    )
)


print(
    "Confusion Matrix:"
)


print(
    confusion_matrix(

        y_valid,

        logistic_predictions,

        labels=CLASS_NAMES
    )
)


# ============================================================
# MODEL 2
# RANDOM FOREST
# ============================================================

print("\n")
print("=" * 75)
print("MODEL 2 - RANDOM FOREST")
print("=" * 75)


random_forest_model = RandomForestClassifier(

    n_estimators=150,

    max_features="sqrt",

    class_weight="balanced",

    random_state=RANDOM_STATE,

    n_jobs=-1
)


print(
    "\nTraining Random Forest..."
)

print(
    "This may take some time..."
)


random_forest_model.fit(

    X_train_features,

    y_train
)


random_forest_predictions = (
    random_forest_model
    .predict(X_valid_features)
)


random_forest_accuracy = accuracy_score(

    y_valid,

    random_forest_predictions
)


random_forest_precision = precision_score(

    y_valid,

    random_forest_predictions,

    average="weighted",

    zero_division=0
)


random_forest_recall = recall_score(

    y_valid,

    random_forest_predictions,

    average="weighted",

    zero_division=0
)


random_forest_f1 = f1_score(

    y_valid,

    random_forest_predictions,

    average="weighted",

    zero_division=0
)


print(
    f"\nAccuracy  : {random_forest_accuracy:.4f}"
)

print(
    f"Precision : {random_forest_precision:.4f}"
)

print(
    f"Recall    : {random_forest_recall:.4f}"
)

print(
    f"F1 Score  : {random_forest_f1:.4f}"
)


print(
    "\nClassification Report:"
)


print(
    classification_report(

        y_valid,

        random_forest_predictions,

        labels=CLASS_NAMES,

        zero_division=0
    )
)


print(
    "Confusion Matrix:"
)


print(
    confusion_matrix(

        y_valid,

        random_forest_predictions,

        labels=CLASS_NAMES
    )
)


# ============================================================
# SAVE RANDOM FOREST MODEL
# ============================================================

print("\nSaving Random Forest model...")

joblib.dump(
    random_forest_model,
    RANDOM_FOREST_MODEL_PATH
)

print(
    "[ok] random_forest_model.pkl"
)


# ============================================================
# MODEL COMPARISON
# ============================================================

print("\n")
print("=" * 75)
print("MODEL COMPARISON")
print("=" * 75)


comparison = [

    {
        "model":
            "Logistic Regression",

        "accuracy":
            logistic_accuracy,

        "precision":
            logistic_precision,

        "recall":
            logistic_recall,

        "f1_score":
            logistic_f1
    },

    {
        "model":
            "Random Forest",

        "accuracy":
            random_forest_accuracy,

        "precision":
            random_forest_precision,

        "recall":
            random_forest_recall,

        "f1_score":
            random_forest_f1
    }
]


comparison_df = pd.DataFrame(
    comparison
)


print(
    "\n"
)

print(
    comparison_df.to_string(
        index=False
    )
)


# ============================================================
# SELECT BEST MODEL
# ============================================================

if logistic_f1 >= random_forest_f1:

    best_model = logistic_model

    best_model_name = (
        "Logistic Regression"
    )

    best_predictions = (
        logistic_predictions
    )

    best_accuracy = (
        logistic_accuracy
    )

    best_precision = (
        logistic_precision
    )

    best_recall = (
        logistic_recall
    )

    best_f1 = (
        logistic_f1
    )

else:

    best_model = random_forest_model

    best_model_name = (
        "Random Forest"
    )

    best_predictions = (
        random_forest_predictions
    )

    best_accuracy = (
        random_forest_accuracy
    )

    best_precision = (
        random_forest_precision
    )

    best_recall = (
        random_forest_recall
    )

    best_f1 = (
        random_forest_f1
    )


print("\n")
print("=" * 75)
print("BEST MODEL")
print("=" * 75)


print(
    "\nBest Model:",
    best_model_name
)

print(
    f"Accuracy  : {best_accuracy:.4f}"
)

print(
    f"Precision : {best_precision:.4f}"
)

print(
    f"Recall    : {best_recall:.4f}"
)

print(
    f"F1 Score  : {best_f1:.4f}"
)


# ============================================================
# FINAL HOLDOUT TEST
# ============================================================

print("\n")
print("=" * 75)
print("FINAL HOLDOUT TEST")
print("=" * 75)


holdout_texts = [

    text

    for text, label
    in HOLDOUT_TESTS
]


holdout_actual = [

    label

    for text, label
    in HOLDOUT_TESTS
]


holdout_cleaned = [

    clean_text(text)

    for text
    in holdout_texts
]


# ------------------------------------------------------------
# Transform holdout data
# ------------------------------------------------------------

holdout_word = (
    word_vectorizer
    .transform(holdout_cleaned)
)


holdout_char = (
    char_vectorizer
    .transform(holdout_cleaned)
)


holdout_features = hstack(

    [
        holdout_word,
        holdout_char
    ]

).tocsr()


# ------------------------------------------------------------
# Predict
# ------------------------------------------------------------

holdout_predictions = (
    best_model
    .predict(holdout_features)
)


# ------------------------------------------------------------
# Metrics
# ------------------------------------------------------------

holdout_accuracy = accuracy_score(

    holdout_actual,

    holdout_predictions
)


holdout_precision = precision_score(

    holdout_actual,

    holdout_predictions,

    average="weighted",

    zero_division=0
)


holdout_recall = recall_score(

    holdout_actual,

    holdout_predictions,

    average="weighted",

    zero_division=0
)


holdout_f1 = f1_score(

    holdout_actual,

    holdout_predictions,

    average="weighted",

    zero_division=0
)


print(
    f"\nHoldout Accuracy  : "
    f"{holdout_accuracy:.4f}"
)

print(
    f"Holdout Precision : "
    f"{holdout_precision:.4f}"
)

print(
    f"Holdout Recall    : "
    f"{holdout_recall:.4f}"
)

print(
    f"Holdout F1 Score  : "
    f"{holdout_f1:.4f}"
)


# ============================================================
# HOLDOUT REPORT
# ============================================================

print(
    "\nHoldout Classification Report:"
)


print(
    classification_report(

        holdout_actual,

        holdout_predictions,

        labels=CLASS_NAMES,

        zero_division=0
    )
)


# ============================================================
# HOLDOUT CONFUSION MATRIX
# ============================================================

print(
    "Holdout Confusion Matrix:"
)


print(
    confusion_matrix(

        holdout_actual,

        holdout_predictions,

        labels=CLASS_NAMES
    )
)


# ============================================================
# HOLDOUT INDIVIDUAL RESULTS
# ============================================================

print("\n")
print("=" * 75)
print("HOLDOUT PREDICTIONS")
print("=" * 75)


for text, actual, predicted in zip(

    holdout_texts,

    holdout_actual,

    holdout_predictions

):

    if actual == predicted:

        status = "[ok]CORRECT"

    else:

        status = "[WRONG]"


    print(
        f"\n{status}"
    )

    print(
        "Actual   :",
        actual
    )

    print(
        "Predicted:",
        predicted
    )

    print(
        "Text     :",
        text
    )


# ============================================================
# CREATE FINAL FEATURE UNION
# ============================================================
#
# This is IMPORTANT for Flask.
#
# vectorizer.pkl will contain ONE object:
#
# FeatureUnion(
#     word_tfidf,
#     char_tfidf
# )
#
# Therefore:
#
# vectorizer.transform([text])
#
# will work in the Flask application.
#
# ============================================================

print("\n")
print(
    "Creating final FeatureUnion..."
)


final_vectorizer = FeatureUnion(

    transformer_list=[

        (
            "word",

            TfidfVectorizer(

                lowercase=True,

                stop_words=None,

                ngram_range=(1, 3),

                min_df=1,

                max_df=0.98,

                max_features=60000,

                sublinear_tf=True
            )
        ),

        (
            "char",

            TfidfVectorizer(

                analyzer="char_wb",

                ngram_range=(3, 5),

                min_df=2,

                max_features=25000,

                sublinear_tf=True
            )
        )
    ]
)


# ============================================================
# FIT FINAL VECTORZIER ON COMPLETE TRAINING DATA
# ============================================================

print(
    "Fitting final vectorizer..."
)


final_features = (
    final_vectorizer
    .fit_transform(
        training_df["clean_text"]
    )
)


print(
    "Final feature shape:",
    final_features.shape
)


# ============================================================
# RETRAIN BEST MODEL ON ALL TRAINING DATA
# ============================================================

print("\n")
print("=" * 75)
print("RETRAINING BEST MODEL ON FULL TRAINING DATA")
print("=" * 75)


if best_model_name == "Logistic Regression":

    final_model = LogisticRegression(

        C=1.5,

        max_iter=3000,

        class_weight="balanced",

        solver="lbfgs",

        random_state=RANDOM_STATE
    )

else:

    final_model = RandomForestClassifier(

        n_estimators=150,

        max_features="sqrt",

        class_weight="balanced",

        random_state=RANDOM_STATE,

        n_jobs=-1
    )


print(
    "\nTraining final model:"
)

print(
    best_model_name
)


final_model.fit(

    final_features,

    training_df[
        "sentiment_label"
    ]
)


# ============================================================
# SAVE MODEL
# ============================================================

print("\nSaving final model...")


joblib.dump(
    
    final_model,

    MODEL_PATH
)

joblib.dump(

    final_vectorizer,

    VECTORIZER_PATH
)


# ============================================================
# SAVE MODEL COMPARISON JSON
# ============================================================

comparison_json = {

    "best_model":
        best_model_name,

    "validation": {

        "accuracy":
            round(
                best_accuracy,
                4
            ),

        "precision":
            round(
                best_precision,
                4
            ),

        "recall":
            round(
                best_recall,
                4
            ),

        "f1_score":
            round(
                best_f1,
                4
            )
    },

    "holdout": {

        "accuracy":
            round(
                holdout_accuracy,
                4
            ),

        "precision":
            round(
                holdout_precision,
                4
            ),

        "recall":
            round(
                holdout_recall,
                4
            ),

        "f1_score":
            round(
                holdout_f1,
                4
            )
    },

    "models": {

        "Logistic Regression": {

            "accuracy":
                round(
                    logistic_accuracy,
                    4
                ),

            "precision":
                round(
                    logistic_precision,
                    4
                ),

            "recall":
                round(
                    logistic_recall,
                    4
                ),

            "f1_score":
                round(
                    logistic_f1,
                    4
                )
        },

        "Random Forest": {

            "accuracy":
                round(
                    random_forest_accuracy,
                    4
                ),

            "precision":
                round(
                    random_forest_precision,
                    4
                ),

            "recall":
                round(
                    random_forest_recall,
                    4
                ),

            "f1_score":
                round(
                    random_forest_f1,
                    4
                )
        }
    }
}


with open(

    COMPARISON_PATH,

    "w",

    encoding="utf-8"

) as file:

    json.dump(

        comparison_json,

        file,

        indent=4
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n")
print("=" * 75)
print("TRAINING COMPLETED SUCCESSFULLY")
print("=" * 75)


print(
    "\nBest Model:",
    best_model_name
)


print(
    f"\nValidation Accuracy:"
    f" {best_accuracy * 100:.2f}%"
)


print(
    f"Validation Precision:"
    f" {best_precision * 100:.2f}%"
)


print(
    f"Validation Recall:"
    f" {best_recall * 100:.2f}%"
)


print(
    f"Validation F1 Score:"
    f" {best_f1 * 100:.2f}%"
)


print(
    f"\nHoldout Accuracy:"
    f" {holdout_accuracy * 100:.2f}%"
)


print(
    f"Holdout Precision:"
    f" {holdout_precision * 100:.2f}%"
)


print(
    f"Holdout Recall:"
    f" {holdout_recall * 100:.2f}%"
)


print(
    f"Holdout F1 Score:"
    f" {holdout_f1 * 100:.2f}%"
)


print("\nSaved files:")

print(
    "[ok]model.pkl"
)

print(
    "[ok] vectorizer.pkl"
)

print(
    "[ok] model_comparison.json"
)


print("\n")
print("=" * 75)
print("VERSION 3 TRAINING FINISHED")
print("=" * 75)

print(
    "\nThe final model has been selected automatically"
)

print(
    "based on validation weighted F1 score."
)

print(
    "\nDo not claim 80%+ accuracy unless the actual"
)

print(
    "training result reaches that level."
)

print(
    "=" * 75
)