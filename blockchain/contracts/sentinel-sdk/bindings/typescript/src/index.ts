import { Buffer } from "buffer";
import { Address } from "@stellar/stellar-sdk";
import {
  AssembledTransaction,
  Client as ContractClient,
  ClientOptions as ContractClientOptions,
  MethodOptions,
  Result,
  Spec as ContractSpec,
} from "@stellar/stellar-sdk/contract";
import type {
  u32,
  i32,
  u64,
  i64,
  u128,
  i128,
  u256,
  i256,
  Option,
  Timepoint,
  Duration,
} from "@stellar/stellar-sdk/contract";
export * from "@stellar/stellar-sdk";
export * as contract from "@stellar/stellar-sdk/contract";
export * as rpc from "@stellar/stellar-sdk/rpc";

if (typeof window !== "undefined") {
  //@ts-ignore Buffer exists
  window.Buffer = window.Buffer || Buffer;
}


export const networks = {
  testnet: {
    networkPassphrase: "Test SDF Network ; September 2015",
    contractId: "CAR3MXRMRSOJLUNCP4L36M4VWBMGWJT5DPBAYEKQYJZEW7VQ6WQPZRDO",
  }
} as const

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
export type RiskDecision = { tag: "Allow", values: void } | { tag: "Limit", values: readonly [u32] } | { tag: "Freeze", values: void };

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
  get_risk: ({ wallet }: { wallet: string }, options?: MethodOptions) => Promise<AssembledTransaction<Option<RiskState>>>

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
  is_frozen: ({ wallet }: { wallet: string }, options?: MethodOptions) => Promise<AssembledTransaction<boolean>>

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
  initialize: ({ oracle_pubkey }: { oracle_pubkey: PublicKey }, options?: MethodOptions) => Promise<AssembledTransaction<null>>

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
  submit_risk: ({ payload, signature }: { payload: RiskPayload, signature: Signature }, options?: MethodOptions) => Promise<AssembledTransaction<null>>

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
  check_permission: ({ wallet }: { wallet: string }, options?: MethodOptions) => Promise<AssembledTransaction<RiskDecision>>

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
  get_oracle_pubkey: (options?: MethodOptions) => Promise<AssembledTransaction<PublicKey>>

}
export class Client extends ContractClient {
  static async deploy<T = Client>(
    /** Options for initializing a Client as well as for calling a method, with extras specific to deploying. */
    options: MethodOptions &
      Omit<ContractClientOptions, "contractId"> & {
        /** The hash of the Wasm blob, which must already be installed on-chain. */
        wasmHash: Buffer | string;
        /** Salt used to generate the contract's ID. Passed through to {@link Operation.createCustomContract}. Default: random. */
        salt?: Buffer | Uint8Array;
        /** The format used to decode `wasmHash`, if it's provided as a string. */
        format?: "hex" | "base64";
      }
  ): Promise<AssembledTransaction<T>> {
    return ContractClient.deploy(null, options)
  }
  constructor(public readonly options: ContractClientOptions) {
    super(
      new ContractSpec(["AAAAAAAAASdRdWVyeSByaXNrIHN0YXRlIGZvciBhIHdhbGxldCAocmVhZC1vbmx5KQoKQW55IGNvbnRyYWN0IGNhbiBjYWxsIHRoaXMgdG8gY2hlY2sgYSB3YWxsZXQncyByaXNrIHN0YXR1cy4KUmV0dXJucyBOb25lIGlmIHdhbGxldCBoYXMgbmV2ZXIgYmVlbiBzY29yZWQuCgojIEFyZ3VtZW50cwoqIGB3YWxsZXRgIC0gQWRkcmVzcyB0byBxdWVyeQoKIyBSZXR1cm5zCiogYFNvbWUoUmlza1N0YXRlKWAgaWYgd2FsbGV0IGhhcyBiZWVuIHNjb3JlZAoqIGBOb25lYCBpZiB3YWxsZXQgaXMgdW5rbm93biAodHJlYXQgYXMgQWxsb3cpAAAAAAhnZXRfcmlzawAAAAEAAAAAAAAABndhbGxldAAAAAAAEwAAAAEAAAPoAAAH0AAAAAlSaXNrU3RhdGUAAAA=",
        "AAAAAAAAAJdDaGVjayBpZiB3YWxsZXQgaXMgZnJvemVuIChjb252ZW5pZW5jZSBmdW5jdGlvbikKCiMgQXJndW1lbnRzCiogYHdhbGxldGAgLSBBZGRyZXNzIHRvIGNoZWNrCgojIFJldHVybnMKKiBgdHJ1ZWAgaWYgd2FsbGV0IGlzIGZyb3plbgoqIGBmYWxzZWAgb3RoZXJ3aXNlAAAAAAlpc19mcm96ZW4AAAAAAAABAAAAAAAAAAZ3YWxsZXQAAAAAABMAAAABAAAAAQ==",
        "AAAAAAAAAPtJbml0aWFsaXplIHRoZSBTREsgd2l0aCBPcmFjbGUncyBwdWJsaWMga2V5CgpUaGlzIG11c3QgYmUgY2FsbGVkIG9uY2UgYWZ0ZXIgZGVwbG95bWVudC4KVGhlIE9yYWNsZSBwdWJsaWMga2V5IGlzIGltbXV0YWJsZSBhZnRlciBpbml0aWFsaXphdGlvbi4KCiMgQXJndW1lbnRzCiogYG9yYWNsZV9wdWJrZXlgIC0gRWQyNTUxOSBwdWJsaWMga2V5IGZyb20gT3JhY2xlIHNlcnZpY2UKCiMgUGFuaWNzCiogSWYgYWxyZWFkeSBpbml0aWFsaXplZAAAAAAKaW5pdGlhbGl6ZQAAAAAAAQAAAAAAAAANb3JhY2xlX3B1YmtleQAAAAAAB9AAAAAJUHVibGljS2V5AAAAAAAAAA==",
        "AAAAAAAAAWtTdWJtaXQgc2lnbmVkIHJpc2sgc2NvcmUgZnJvbSBPcmFjbGUKCk9ubHkgdGhlIE9yYWNsZSBjYW4gY2FsbCB0aGlzICh2ZXJpZmllZCBieSBzaWduYXR1cmUpLgpVcGRhdGVzIHRoZSBvbi1jaGFpbiByaXNrIHN0YXRlIGZvciBhIHdhbGxldC4KCiMgQXJndW1lbnRzCiogYHBheWxvYWRgIC0gUmlzayBkYXRhICh3YWxsZXQsIHNjb3JlLCB0aW1lc3RhbXApCiogYHNpZ25hdHVyZWAgLSBFZDI1NTE5IHNpZ25hdHVyZSBmcm9tIE9yYWNsZQoKIyBQYW5pY3MKKiBJZiBzaWduYXR1cmUgaXMgaW52YWxpZAoqIElmIHRpbWVzdGFtcCBpcyB0b28gb2xkICg+NSBtaW51dGVzKQoqIElmIHJpc2sgc2NvcmUgaXMgb3V0IG9mIHJhbmdlICgwLTEwMCkAAAAAC3N1Ym1pdF9yaXNrAAAAAAIAAAAAAAAAB3BheWxvYWQAAAAH0AAAAAtSaXNrUGF5bG9hZAAAAAAAAAAACXNpZ25hdHVyZQAAAAAAB9AAAAAJU2lnbmF0dXJlAAAAAAAAAA==",
        "AAAAAAAAAWRDaGVjayBwZXJtaXNzaW9uIGRlY2lzaW9uIGZvciBhIHdhbGxldCAoU0RLIGNvcmUgZnVuY3Rpb24pCgpUaGlzIGlzIHRoZSBtYWluIGZ1bmN0aW9uIGludGVncmF0aW5nIHByb3RvY29scyBjYWxsLgpSZXR1cm5zIHRoZSByaXNrIGRlY2lzaW9uIHdpdGhvdXQgZW5mb3JjaW5nIGl0LgoKIyBBcmd1bWVudHMKKiBgd2FsbGV0YCAtIEFkZHJlc3MgdG8gY2hlY2sKCiMgUmV0dXJucwoqIGBSaXNrRGVjaXNpb25gIC0gQWxsb3csIExpbWl0KGFtb3VudCksIG9yIEZyZWV6ZQoKIyBEZWZhdWx0IEJlaGF2aW9yCiogSWYgd2FsbGV0IGlzIHVua25vd24sIHJldHVybnMgYEFsbG93YCAoaW5ub2NlbnQgdW50aWwgcHJvdmVuIHJpc2t5KQAAABBjaGVja19wZXJtaXNzaW9uAAAAAQAAAAAAAAAGd2FsbGV0AAAAAAATAAAAAQAAB9AAAAAMUmlza0RlY2lzaW9u",
        "AAAAAAAAAKlHZXQgT3JhY2xlJ3MgcHVibGljIGtleSAocmVhZC1vbmx5KQoKUmV0dXJucyB0aGUgRWQyNTUxOSBwdWJsaWMga2V5IHVzZWQgdG8gdmVyaWZ5IE9yYWNsZSBzaWduYXR1cmVzLgoKIyBSZXR1cm5zCiogT3JhY2xlJ3MgcHVibGljIGtleQoKIyBQYW5pY3MKKiBJZiBTREsgbm90IGluaXRpYWxpemVkAAAAAAAAEWdldF9vcmFjbGVfcHVia2V5AAAAAAAAAAAAAAEAAAfQAAAACVB1YmxpY0tleQAAAA==",
        "AAAAAQAAADBDb21wbGV0ZSByaXNrIHN0YXRlIGZvciBhIHdhbGxldCBzdG9yZWQgb24tY2hhaW4AAAAAAAAACVJpc2tTdGF0ZQAAAAAAAAMAAAAlQ29tcHV0ZWQgZGVjaXNpb24gYmFzZWQgb24gcmlzayBzY29yZQAAAAAAAAhkZWNpc2lvbgAAB9AAAAAMUmlza0RlY2lzaW9uAAAAHVVuaXggdGltZXN0YW1wIG9mIGxhc3QgdXBkYXRlAAAAAAAADGxhc3RfdXBkYXRlZAAAAAYAAAAVUmlzayBzY29yZSBmcm9tIDAtMTAwAAAAAAAACnJpc2tfc2NvcmUAAAAAAAQ=",
        "AAAAAQAAAC1QYXlsb2FkIHNpZ25lZCBieSBPcmFjbGUgKHdoYXQgZ2V0cyB2ZXJpZmllZCkAAAAAAAAAAAAAC1Jpc2tQYXlsb2FkAAAAAAMAAAAVUmlzayBzY29yZSBmcm9tIDAtMTAwAAAAAAAACnJpc2tfc2NvcmUAAAAAAAQAAAAmVW5peCB0aW1lc3RhbXAgd2hlbiBPcmFjbGUgc2lnbmVkIHRoaXMAAAAAAAl0aW1lc3RhbXAAAAAAAAAGAAAAG1dhbGxldCBhZGRyZXNzIGJlaW5nIHNjb3JlZAAAAAAGd2FsbGV0AAAAAAAT",
        "AAAAAgAAADhEZWNpc2lvbiByZXR1cm5lZCB0byBwcm90b2NvbHMgYWJvdXQgd2hhdCBhY3Rpb24gdG8gdGFrZQAAAAAAAAAMUmlza0RlY2lzaW9uAAAAAwAAAAAAAAAlV2FsbGV0IGlzIHNhZmUgLSBhbGxvdyBhbGwgb3BlcmF0aW9ucwAAAAAAAAVBbGxvdwAAAAAAAAEAAAA0V2FsbGV0IGhhcyBtb2RlcmF0ZSByaXNrIC0gbGltaXQgdG8gc3BlY2lmaWVkIGFtb3VudAAAAAVMaW1pdAAAAAAAAAEAAAAEAAAAAAAAACtXYWxsZXQgaXMgaGlnaCByaXNrIC0gZnJlZXplIGFsbCBvcGVyYXRpb25zAAAAAAZGcmVlemUAAA=="]),
      options
    )
  }
  public readonly fromJSON = {
    get_risk: this.txFromJSON<Option<RiskState>>,
    is_frozen: this.txFromJSON<boolean>,
    initialize: this.txFromJSON<null>,
    submit_risk: this.txFromJSON<null>,
    check_permission: this.txFromJSON<RiskDecision>,
    get_oracle_pubkey: this.txFromJSON<PublicKey>
  }
}