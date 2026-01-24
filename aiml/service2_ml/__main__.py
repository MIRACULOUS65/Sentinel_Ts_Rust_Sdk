"""
Main CLI Entry Point
Provides commands for generating data, training, and running the API.
"""
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Sentinel ML Risk Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate synthetic data
  python -m service4_ml generate --wallets 500 --hours 48
  
  # Train the model
  python -m service4_ml train --dataset synthetic_dataset.jsonl
  
  # Run the API server
  python -m service4_ml serve --port 8084
  
  # Quick test
  python -m service4_ml test --wallet GABCD...
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate synthetic data")
    gen_parser.add_argument("--wallets", type=int, default=500, help="Number of wallets")
    gen_parser.add_argument("--hours", type=int, default=48, help="Duration in hours")
    gen_parser.add_argument("--seed", type=int, default=42, help="Random seed")
    gen_parser.add_argument("--output", type=str, default="synthetic_dataset.jsonl")
    gen_parser.add_argument("--anomaly-ratio", type=float, default=0.5)
    
    # Train command
    train_parser = subparsers.add_parser("train", help="Train the model")
    train_parser.add_argument("--dataset", type=str, default="synthetic_dataset.jsonl")
    train_parser.add_argument("--model-dir", type=str, default="models")
    train_parser.add_argument("--min-txs", type=int, default=5)
    train_parser.add_argument("--val-split", type=float, default=0.2)
    
    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Run API server")
    serve_parser.add_argument("--host", type=str, default="0.0.0.0")
    serve_parser.add_argument("--port", type=int, default=8084)
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test a specific wallet")
    test_parser.add_argument("--wallet", type=str, required=True)
    test_parser.add_argument("--dataset", type=str, default="synthetic_dataset.jsonl")
    test_parser.add_argument("--model-dir", type=str, default="models")
    
    # Parse args
    args = parser.parse_args()
    
    if args.command == "generate":
        from .synthetic_data.generator import SyntheticGenerator
        
        generator = SyntheticGenerator(
            num_wallets=args.wallets,
            duration_hours=args.hours,
            seed=args.seed,
            anomaly_ratio=args.anomaly_ratio
        )
        generator.generate(args.output)
    
    elif args.command == "train":
        from .ml_engine.train import train_from_dataset
        
        train_from_dataset(
            dataset_path=args.dataset,
            model_dir=args.model_dir,
            min_wallet_txs=args.min_txs,
            validation_split=args.val_split
        )
    
    elif args.command == "serve":
        from .ml_engine.api import run_server
        
        run_server(host=args.host, port=args.port)
    
    elif args.command == "test":
        from .ml_engine.ingest import load_jsonl
        from .ml_engine.state_manager import WalletStateManager
        from .ml_engine.risk_engine import RiskEngine
        
        print("Loading dataset...")
        txs = load_jsonl(args.dataset)
        
        print("Building state...")
        state = WalletStateManager()
        for tx in txs:
            state.add_transaction(tx)
        
        print("Loading model...")
        engine = RiskEngine()
        engine.load(args.model_dir)
        
        print(f"\nPredicting for wallet: {args.wallet}")
        score, reason, details = engine.predict(args.wallet, state)
        
        print(f"\n{'='*50}")
        print(f"🎯 RISK ASSESSMENT")
        print(f"{'='*50}")
        print(f"Wallet: {args.wallet[:20]}...")
        print(f"Risk Score: {score}/100")
        print(f"Reason: {reason}")
        print(f"\nPattern Scores:")
        for pattern, pscore in details.get("pattern_details", {}).items():
            print(f"   {pattern}: {pscore}/100")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
