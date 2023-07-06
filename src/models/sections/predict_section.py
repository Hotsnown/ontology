new_documents = ['Some new document 1', 'Another new document 2']
predictions = pipeline.predict(new_documents)
for document, prediction in zip(new_documents, predictions):
    print(f"Document: {document}")
    print(f"Predicted Label: {prediction}")
    print("\n---\n")