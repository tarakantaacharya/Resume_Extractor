"""
Train custom NER model for resume skill extraction
"""
import json
import random
import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

class ResumeNERTrainer:
    def __init__(self, model_name="en_core_web_sm"):
        self.model_name = model_name
        self.nlp = None
        self.training_losses = []
        
    def load_training_data(self, data_file: str):
        """Load training data from JSON file"""
        with open(data_file, 'r', encoding='utf-8') as f:
            training_data = json.load(f)
        
        print(f"Loaded {len(training_data)} training examples")
        return training_data
    
    def prepare_model(self, labels: list):
        """Prepare the spaCy model for training"""
        try:
            # Load existing model
            self.nlp = spacy.load(self.model_name)
            print(f"Loaded existing model: {self.model_name}")
        except OSError:
            # Create blank model if base model not found
            print(f"Model {self.model_name} not found. Creating blank model.")
            self.nlp = spacy.blank("en")
        
        # Get or create NER component
        if "ner" not in self.nlp.pipe_names:
            ner = self.nlp.add_pipe("ner")
        else:
            ner = self.nlp.get_pipe("ner")
        
        # Add labels to NER
        for label in labels:
            ner.add_label(label)
        
        return self.nlp
    
    def convert_to_examples(self, training_data):
        """Convert training data to spaCy Example objects"""
        examples = []
        for text, annotations in training_data:
            doc = self.nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            examples.append(example)
        return examples
    
    def train_model(self, training_data, n_iter=30, drop_rate=0.2):
        """Train the NER model"""
        # Prepare labels
        labels = set()
        for text, annotations in training_data:
            for start, end, label in annotations["entities"]:
                labels.add(label)
        
        labels = list(labels)
        print(f"Training labels: {labels}")
        
        # Prepare model
        self.nlp = self.prepare_model(labels)
        
        # Convert to examples
        examples = self.convert_to_examples(training_data)
        
        # Split into train and validation
        random.shuffle(examples)
        split_idx = int(0.8 * len(examples))
        train_examples = examples[:split_idx]
        val_examples = examples[split_idx:]
        
        print(f"Training examples: {len(train_examples)}")
        print(f"Validation examples: {len(val_examples)}")
        
        # Get only NER component for training
        pipe_exceptions = ["ner"]
        unaffected_pipes = [pipe for pipe in self.nlp.pipe_names if pipe not in pipe_exceptions]
        
        # Training loop
        with self.nlp.disable_pipes(*unaffected_pipes):
            optimizer = self.nlp.begin_training()
            
            for iteration in range(n_iter):
                print(f"Iteration {iteration + 1}/{n_iter}")
                
                losses = {}
                random.shuffle(train_examples)
                
                # Create batches
                batches = minibatch(train_examples, size=compounding(4.0, 32.0, 1.001))
                
                for batch in batches:
                    self.nlp.update(batch, drop=drop_rate, losses=losses, sgd=optimizer)
                
                # Store training loss
                train_loss = losses.get("ner", 0)
                self.training_losses.append(train_loss)
                
                # Evaluate on validation set every 5 iterations
                if (iteration + 1) % 5 == 0:
                    val_score = self.evaluate_model(val_examples)
                    print(f"  Training Loss: {train_loss:.4f}")
                    print(f"  Validation Score: {val_score:.4f}")
                else:
                    print(f"  Training Loss: {train_loss:.4f}")
        
        print("Training completed!")
        
        # Final evaluation
        final_score = self.evaluate_model(val_examples)
        print(f"Final Validation Score: {final_score:.4f}")
        
        return self.nlp
    
    def evaluate_model(self, examples):
        """Evaluate the model on given examples"""
        scores = self.nlp.evaluate(examples)
        return scores["ents_f"]
    
    def save_model(self, output_dir):
        """Save the trained model"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        self.nlp.to_disk(output_path)
        print(f"Model saved to {output_path}")
    
    def plot_training_curve(self, save_path=None):
        """Plot training loss curve"""
        plt.figure(figsize=(10, 6))
        plt.plot(range(1, len(self.training_losses) + 1), self.training_losses, 'b-', linewidth=2)
        plt.title('NER Training Loss Over Time', fontsize=16)
        plt.xlabel('Iteration', fontsize=12)
        plt.ylabel('Training Loss', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Training curve saved to {save_path}")
        
        plt.show()
    
    def test_model(self, test_texts):
        """Test the model on sample texts"""
        print("\n" + "="*50)
        print("TESTING TRAINED MODEL")
        print("="*50)
        
        for i, text in enumerate(test_texts, 1):
            print(f"\nTest {i}:")
            print(f"Text: {text[:100]}...")
            
            doc = self.nlp(text)
            entities = [(ent.text, ent.label_) for ent in doc.ents]
            
            if entities:
                print("Extracted entities:")
                for entity_text, label in entities:
                    print(f"  {label}: {entity_text}")
            else:
                print("No entities found")

def main():
    """Main training function"""
    # Initialize trainer
    trainer = ResumeNERTrainer()
    
    # Load training data
    data_file = "d:/.vscode/Resume_Extractor/annotations/training_data.json"
    training_data = trainer.load_training_data(data_file)
    
    # Train model
    print("\nStarting training...")
    trained_model = trainer.train_model(training_data, n_iter=25)
    
    # Save model
    model_output_dir = "d:/.vscode/Resume_Extractor/models/resume_ner_model"
    trainer.save_model(model_output_dir)
    
    # Plot training curve
    plot_path = "d:/.vscode/Resume_Extractor/models/training_curve.png"
    trainer.plot_training_curve(plot_path)
    
    # Test the model
    test_texts = [
        """John Doe
        Software Engineer with 3 years of experience at Google.
        Skills: Python, Machine Learning, TensorFlow, AWS
        Education: B.Tech in Computer Science from MIT
        """,
        """Sarah Smith
        Data Scientist at Microsoft for 2 years.
        Expertise in Deep Learning, PyTorch, SQL, and Azure.
        M.S. in Data Science from Stanford University.
        """
    ]
    
    trainer.test_model(test_texts)

if __name__ == "__main__":
    main()