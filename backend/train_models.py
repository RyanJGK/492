"""Train AI models for anomaly detection."""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from pathlib import Path
import pickle
import logging

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
except ImportError:
    print("TensorFlow not available")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_synthetic_training_data():
    """Generate synthetic 'normal' behavior data for model training."""
    logger.info("Generating synthetic training data...")
    
    # Authentication: Normal login patterns
    auth_normal = pd.DataFrame({
        'failed_login_rate': np.random.normal(2, 1, 1000),  # 2 failures per hour is normal
        'geo_velocity': np.random.randint(1, 3, 1000),  # 1-2 locations is normal
        'time_anomaly': np.random.uniform(0, 0.2, 1000),  # <20% off-hours is normal
        'enumeration_score': np.random.uniform(0, 0.3, 1000)  # <30% username variety is normal
    })
    
    # Network: Normal traffic patterns
    network_normal = pd.DataFrame({
        'data_volume': np.random.normal(50, 20, 1000),  # 50 MB/hour average
        'connection_pattern': np.random.uniform(0.1, 0.4, 1000),  # 10-40% unique destinations
        'port_entropy': np.random.normal(2.5, 0.5, 1000),  # Moderate port diversity
        'protocol_anomaly': np.random.uniform(0.2, 0.5, 1000)  # 20-50% protocol diversity
    })
    
    # Vulnerability: Normal patch status
    vuln_normal = pd.DataFrame({
        'cvss_score': np.random.uniform(0, 6, 1000),  # Low-medium severity
        'exploit_available': np.random.choice([0, 1], 1000, p=[0.9, 0.1]),  # 10% have exploits
        'asset_criticality': np.random.uniform(0.3, 0.7, 1000)  # Mixed criticality
    })
    
    return auth_normal, network_normal, vuln_normal


def train_isolation_forest_auth(X_train):
    """Train Isolation Forest for authentication anomaly detection."""
    logger.info("Training Isolation Forest for authentication...")
    
    model = IsolationForest(
        n_estimators=100,
        contamination=0.1,  # Expect 10% anomalies
        random_state=42
    )
    
    model.fit(X_train)
    
    # Test prediction
    predictions = model.predict(X_train[:10])
    logger.info(f"Sample predictions: {predictions}")
    
    return model


def build_lstm_autoencoder_network(input_dim, sequence_length=10):
    """Build LSTM Autoencoder for network traffic anomaly detection."""
    logger.info("Building LSTM Autoencoder for network traffic...")
    
    # Encoder
    encoder_inputs = keras.Input(shape=(sequence_length, input_dim))
    encoder_lstm1 = layers.LSTM(64, activation='relu', return_sequences=True)(encoder_inputs)
    encoder_lstm2 = layers.LSTM(32, activation='relu', return_sequences=False)(encoder_lstm1)
    
    # Decoder
    decoder_repeat = layers.RepeatVector(sequence_length)(encoder_lstm2)
    decoder_lstm1 = layers.LSTM(32, activation='relu', return_sequences=True)(decoder_repeat)
    decoder_lstm2 = layers.LSTM(64, activation='relu', return_sequences=True)(decoder_lstm1)
    decoder_outputs = layers.TimeDistributed(layers.Dense(input_dim))(decoder_lstm2)
    
    # Autoencoder model
    autoencoder = keras.Model(encoder_inputs, decoder_outputs, name='lstm_autoencoder')
    autoencoder.compile(optimizer='adam', loss='mse')
    
    logger.info(f"Model summary:")
    autoencoder.summary()
    
    return autoencoder


def train_lstm_autoencoder(X_train):
    """Train LSTM Autoencoder on network data."""
    logger.info("Training LSTM Autoencoder...")
    
    # Reshape data for LSTM (samples, timesteps, features)
    sequence_length = 10
    n_features = X_train.shape[1]
    
    # Create sequences
    sequences = []
    for i in range(len(X_train) - sequence_length):
        sequences.append(X_train[i:i+sequence_length])
    
    X_sequences = np.array(sequences)
    logger.info(f"Training on {len(X_sequences)} sequences of shape {X_sequences.shape}")
    
    # Build and train model
    model = build_lstm_autoencoder_network(n_features, sequence_length)
    
    history = model.fit(
        X_sequences, X_sequences,
        epochs=50,
        batch_size=32,
        validation_split=0.2,
        verbose=1
    )
    
    logger.info(f"Final training loss: {history.history['loss'][-1]:.4f}")
    logger.info(f"Final validation loss: {history.history['val_loss'][-1]:.4f}")
    
    return model


def train_gradient_boosting_vuln(X_train, y_train):
    """Train Gradient Boosting for vulnerability risk assessment."""
    logger.info("Training Gradient Boosting for vulnerabilities...")
    
    model = GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=3,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # Test prediction
    predictions = model.predict_proba(X_train[:10])
    logger.info(f"Sample prediction probabilities:\n{predictions}")
    
    score = model.score(X_train, y_train)
    logger.info(f"Training accuracy: {score:.4f}")
    
    return model


def save_models(models_dir="./models"):
    """Generate synthetic data, train models, and save them."""
    models_path = Path(models_dir)
    models_path.mkdir(exist_ok=True)
    
    logger.info("=" * 60)
    logger.info("Energy Defense - Model Training")
    logger.info("=" * 60)
    
    # Generate training data
    auth_data, network_data, vuln_data = generate_synthetic_training_data()
    
    # Train Isolation Forest for authentication
    auth_model = train_isolation_forest_auth(auth_data.values)
    with open(models_path / "isolation_forest_auth.pkl", 'wb') as f:
        pickle.dump(auth_model, f)
    logger.info("✓ Saved authentication model")
    
    # Train LSTM Autoencoder for network traffic
    try:
        network_model = train_lstm_autoencoder(network_data.values)
        network_model.save(models_path / "lstm_autoencoder_network.h5")
        logger.info("✓ Saved network model")
    except Exception as e:
        logger.warning(f"Could not train LSTM model: {e}")
    
    # Train Gradient Boosting for vulnerabilities
    # Create labels: high risk (1) if CVSS > 7 AND exploit available
    y_vuln = ((vuln_data['cvss_score'] > 7) & (vuln_data['exploit_available'] == 1)).astype(int)
    vuln_model = train_gradient_boosting_vuln(vuln_data.values, y_vuln.values)
    with open(models_path / "gradient_boosting_vuln.pkl", 'wb') as f:
        pickle.dump(vuln_model, f)
    logger.info("✓ Saved vulnerability model")
    
    # Save scalers
    scalers = {
        'auth': StandardScaler().fit(auth_data.values),
        'network': StandardScaler().fit(network_data.values),
        'vuln': StandardScaler().fit(vuln_data.values)
    }
    
    with open(models_path / "scalers.pkl", 'wb') as f:
        pickle.dump(scalers, f)
    logger.info("✓ Saved feature scalers")
    
    logger.info("=" * 60)
    logger.info("Model training complete!")
    logger.info(f"Models saved to {models_path.absolute()}")
    logger.info("=" * 60)


if __name__ == "__main__":
    save_models("/workspace/models")
