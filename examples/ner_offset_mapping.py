"""Named Entity Recognition (NER) with Offset Mapping.

This example demonstrates how to use tokenize_normalized() for NER tasks,
where you need normalized tokens but also need to know their exact position
in the original text for labeling.
"""

from durak import tokenize_normalized


def demonstrate_ner_workflow():
    """Show a realistic NER workflow using Durak's offset mapping."""
    
    # Sample text with entities
    text = "Ahmet İstanbul'a gitti. Ayşe Ankara'dan geldi."
    
    print("Original text:")
    print(f"  {text!r}\n")
    
    # Tokenize with normalization and offset mapping
    tokens = tokenize_normalized(text)
    
    print("Normalized tokens with offsets:")
    print("  Token            Original         Offsets")
    print("  " + "-" * 52)
    
    for token in tokens:
        original = text[token.start:token.end]
        print(f"  {token.text:15} → {original:15} [{token.start}:{token.end}]")
    
    print("\nNER Labeling Example:")
    print("  Let's say we detect 'ahmet' and 'ayşe' as persons (PER),")
    print("  and 'istanbul'a' and 'ankara'dan' as locations (LOC):\n")
    
    # Simulated NER predictions (in practice, this comes from a model)
    # Format: (token_index, entity_type)
    predictions = [
        (0, "PER"),      # ahmet
        (1, "LOC"),      # istanbul'a
        (5, "PER"),      # ayşe
        (6, "LOC"),      # ankara'dan
    ]
    
    # Apply labels using original text positions
    for token_idx, entity_type in predictions:
        token = tokens[token_idx]
        original_text = text[token.start:token.end]
        print(f"  {original_text:15} ({entity_type}) at position [{token.start}:{token.end}]")
    
    print("\n" + "="*60)
    print("Key Benefits for NER:")
    print("  1. Tokens are normalized for model consistency")
    print("     ('İstanbul' → 'istanbul', 'AHMET' → 'ahmet')")
    print("  2. Offsets point to ORIGINAL text for labeling")
    print("     (preserves proper nouns' original case)")
    print("  3. Compatible with Transformers/spaCy/Flair pipelines")
    print("="*60)


def huggingface_integration_example():
    """Show how to prepare data for Hugging Face Transformers."""
    
    print("\n\nHugging Face Transformers Integration:\n")
    
    text = "Fatih Burak Karagöz İstanbul Teknik Üniversitesi'nde çalışıyor."
    tokens = tokenize_normalized(text)
    
    print(f"Original: {text}\n")
    
    # Format compatible with datasets library
    token_list = []
    ner_tags = []  # Placeholder - would come from annotation
    
    for token in tokens:
        if token.text.strip():  # Skip pure punctuation for this example
            token_list.append(token.text)
            # In real scenario, you'd map these to BIO tags
            ner_tags.append("O")  # Outside entity (placeholder)
    
    print("Token list for model input:")
    print(f"  {token_list}\n")
    
    print("Creating dataset entry:")
    dataset_entry = {
        "tokens": token_list,
        "ner_tags": ner_tags,
        "original_text": text,
        "offsets": [(t.start, t.end) for t in tokens if t.text.strip()],
    }
    
    for key, value in dataset_entry.items():
        if key == "offsets":
            print(f"  {key}: (showing first 3) {value[:3]}...")
        else:
            print(f"  {key}: {value if len(str(value)) < 60 else str(value)[:57] + '...'}")
    
    print("\n✓ Ready to feed into Hugging Face's TokenClassification pipeline!")


def turkish_specific_edge_cases():
    """Demonstrate Turkish-specific tokenization challenges."""
    
    print("\n\nTurkish-Specific Edge Cases:\n")
    
    test_cases = [
        ("İyi", "iyi", "Dotted İ → lowercase i"),
        ("IŞIK", "ışık", "Undotted I → lowercase ı"),
        ("gül'ü", "gül'ü", "Apostrophe in suffix"),
        ("İstanbul'un", "istanbul'un", "Capital İ + apostrophe"),
    ]
    
    for original, expected_normalized, description in test_cases:
        tokens = tokenize_normalized(original)
        actual_normalized = tokens[0].text if tokens else ""
        status = "✓" if actual_normalized == expected_normalized else "✗"
        
        print(f"  {status} {description:30} | {original:15} → {actual_normalized}")


if __name__ == "__main__":
    demonstrate_ner_workflow()
    huggingface_integration_example()
    turkish_specific_edge_cases()
