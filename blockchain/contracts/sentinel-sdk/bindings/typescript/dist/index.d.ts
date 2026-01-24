import { Buffer } from "buffer";
import { AssembledTransaction, Client as ContractClient, ClientOptions as ContractClientOptions, MethodOptions } from "@stellar/stellar-sdk/contract";
import type { u32, u64, Option } from "@stellar/stellar-sdk/contract";
export * from "@stellar/stellar-sdk";
export * as contract from "@stellar/stellar-sdk/contract";
export * as rpc from "@stellar/stellar-sdk/rpc";
export declare const networks: {
    readonly testnet: {
        readonly networkPassphrase: "Test SDF Network ; September 2015";
        readonly contractId: "CAR3MXRMRSOJLUNCP4L36M4VWBMGWJT5DPBAYEKQYJZEW7VQ6WQPZRDO";
    };
};
/**
 * Ed25519 public key type (32 bytes)
 */
export type PublicKey = Buffer;
/**
 * Ed25519 signature type (64 bytes)
 */
export type Signature = Buffer;
/**
 * Complete risk state for a wallet stored on-chain
 */
export interface RiskState {
    /**
   * Computed decision based on risk score
   */
    decision: RiskDecision;
    /**
   * Unix timestamp of last update
   */
    last_updated: u64;
    /**
   * Risk score from 0-100
   */
    risk_score: u32;
}
/**
 * Payload signed by Oracle (what gets verified)
 */
export interface RiskPayload {
    /**
   * Risk score from 0-100
   */
    risk_score: u32;
    /**
   * Unix timestamp when Oracle signed this
   */
    timestamp: u64;
    /**
   * Wallet address being scored
   */
    wallet: string;
}
/**
 * Decision returned to protocols about what action to take
 */
export type RiskDecision = {
    tag: "Allow";
    values: void;
} | {
    tag: "Limit";
    values: readonly [u32];
} | {
    tag: "Freeze";
    values: void;
};
export interface Client {
    /**
     * Construct and simulate a get_risk transaction. Returns an `AssembledTransaction` object which will have a `result` field containing the result of the simulation. If this transaction changes contract state, you will need to call `signAndSend()` on the returned object.
     * Query risk state for a wallet (read-only)
     *
     * Any contract can call this to check a wallet's risk status.
     * Returns None if wallet has never been scored.
     *
     * # Arguments
     * * `wallet` - Address to query
     *
     * # Returns
     * * `Some(RiskState)` if wallet has been scored
     * * `None` if wallet is unknown (treat as Allow)
     */
    get_risk: ({ wallet }: {
        wallet: string;
    }, options?: MethodOptions) => Promise<AssembledTransaction<Option<RiskState>>>;
    /**
     * Construct and simulate a is_frozen transaction. Returns an `AssembledTransaction` object which will have a `result` field containing the result of the simulation. If this transaction changes contract state, you will need to call `signAndSend()` on the returned object.
     * Check if wallet is frozen (convenience function)
     *
     * # Arguments
     * * `wallet` - Address to check
     *
     * # Returns
     * * `true` if wallet is frozen
     * * `false` otherwise
     */
    is_frozen: ({ wallet }: {
        wallet: string;
    }, options?: MethodOptions) => Promise<AssembledTransaction<boolean>>;
    /**
     * Construct and simulate a initialize transaction. Returns an `AssembledTransaction` object which will have a `result` field containing the result of the simulation. If this transaction changes contract state, you will need to call `signAndSend()` on the returned object.
     * Initialize the SDK with Oracle's public key
     *
     * This must be called once after deployment.
     * The Oracle public key is immutable after initialization.
     *
     * # Arguments
     * * `oracle_pubkey` - Ed25519 public key from Oracle service
     *
     * # Panics
     * * If already initialized
     */
    initialize: ({ oracle_pubkey }: {
        oracle_pubkey: PublicKey;
    }, options?: MethodOptions) => Promise<AssembledTransaction<null>>;
    /**
     * Construct and simulate a submit_risk transaction. Returns an `AssembledTransaction` object which will have a `result` field containing the result of the simulation. If this transaction changes contract state, you will need to call `signAndSend()` on the returned object.
     * Submit signed risk score from Oracle
     *
     * Only the Oracle can call this (verified by signature).
     * Updates the on-chain risk state for a wallet.
     *
     * # Arguments
     * * `payload` - Risk data (wallet, score, timestamp)
     * * `signature` - Ed25519 signature from Oracle
     *
     * # Panics
     * * If signature is invalid
     * * If timestamp is too old (>5 minutes)
     * * If risk score is out of range (0-100)
     */
    submit_risk: ({ payload, signature }: {
        payload: RiskPayload;
        signature: Signature;
    }, options?: MethodOptions) => Promise<AssembledTransaction<null>>;
    /**
     * Construct and simulate a check_permission transaction. Returns an `AssembledTransaction` object which will have a `result` field containing the result of the simulation. If this transaction changes contract state, you will need to call `signAndSend()` on the returned object.
     * Check permission decision for a wallet (SDK core function)
     *
     * This is the main function integrating protocols call.
     * Returns the risk decision without enforcing it.
     *
     * # Arguments
     * * `wallet` - Address to check
     *
     * # Returns
     * * `RiskDecision` - Allow, Limit(amount), or Freeze
     *
     * # Default Behavior
     * * If wallet is unknown, returns `Allow` (innocent until proven risky)
     */
    check_permission: ({ wallet }: {
        wallet: string;
    }, options?: MethodOptions) => Promise<AssembledTransaction<RiskDecision>>;
    /**
     * Construct and simulate a get_oracle_pubkey transaction. Returns an `AssembledTransaction` object which will have a `result` field containing the result of the simulation. If this transaction changes contract state, you will need to call `signAndSend()` on the returned object.
     * Get Oracle's public key (read-only)
     *
     * Returns the Ed25519 public key used to verify Oracle signatures.
     *
     * # Returns
     * * Oracle's public key
     *
     * # Panics
     * * If SDK not initialized
     */
    get_oracle_pubkey: (options?: MethodOptions) => Promise<AssembledTransaction<PublicKey>>;
}
export declare class Client extends ContractClient {
    readonly options: ContractClientOptions;
    static deploy<T = Client>(
    /** Options for initializing a Client as well as for calling a method, with extras specific to deploying. */
    options: MethodOptions & Omit<ContractClientOptions, "contractId"> & {
        /** The hash of the Wasm blob, which must already be installed on-chain. */
        wasmHash: Buffer | string;
        /** Salt used to generate the contract's ID. Passed through to {@link Operation.createCustomContract}. Default: random. */
        salt?: Buffer | Uint8Array;
        /** The format used to decode `wasmHash`, if it's provided as a string. */
        format?: "hex" | "base64";
    }): Promise<AssembledTransaction<T>>;
    constructor(options: ContractClientOptions);
    readonly fromJSON: {
        get_risk: (json: string) => AssembledTransaction<Option<RiskState>>;
        is_frozen: (json: string) => AssembledTransaction<boolean>;
        initialize: (json: string) => AssembledTransaction<null>;
        submit_risk: (json: string) => AssembledTransaction<null>;
        check_permission: (json: string) => AssembledTransaction<RiskDecision>;
        get_oracle_pubkey: (json: string) => AssembledTransaction<Buffer>;
    };
}
