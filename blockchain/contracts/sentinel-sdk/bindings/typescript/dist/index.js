import { Buffer } from "buffer";
import { Client as ContractClient, Spec as ContractSpec, } from "@stellar/stellar-sdk/contract";
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
};
export class Client extends ContractClient {
    options;
    static async deploy(
    /** Options for initializing a Client as well as for calling a method, with extras specific to deploying. */
    options) {
        return ContractClient.deploy(null, options);
    }
    constructor(options) {
        super(new ContractSpec(["AAAAAAAAASdRdWVyeSByaXNrIHN0YXRlIGZvciBhIHdhbGxldCAocmVhZC1vbmx5KQoKQW55IGNvbnRyYWN0IGNhbiBjYWxsIHRoaXMgdG8gY2hlY2sgYSB3YWxsZXQncyByaXNrIHN0YXR1cy4KUmV0dXJucyBOb25lIGlmIHdhbGxldCBoYXMgbmV2ZXIgYmVlbiBzY29yZWQuCgojIEFyZ3VtZW50cwoqIGB3YWxsZXRgIC0gQWRkcmVzcyB0byBxdWVyeQoKIyBSZXR1cm5zCiogYFNvbWUoUmlza1N0YXRlKWAgaWYgd2FsbGV0IGhhcyBiZWVuIHNjb3JlZAoqIGBOb25lYCBpZiB3YWxsZXQgaXMgdW5rbm93biAodHJlYXQgYXMgQWxsb3cpAAAAAAhnZXRfcmlzawAAAAEAAAAAAAAABndhbGxldAAAAAAAEwAAAAEAAAPoAAAH0AAAAAlSaXNrU3RhdGUAAAA=",
            "AAAAAAAAAJdDaGVjayBpZiB3YWxsZXQgaXMgZnJvemVuIChjb252ZW5pZW5jZSBmdW5jdGlvbikKCiMgQXJndW1lbnRzCiogYHdhbGxldGAgLSBBZGRyZXNzIHRvIGNoZWNrCgojIFJldHVybnMKKiBgdHJ1ZWAgaWYgd2FsbGV0IGlzIGZyb3plbgoqIGBmYWxzZWAgb3RoZXJ3aXNlAAAAAAlpc19mcm96ZW4AAAAAAAABAAAAAAAAAAZ3YWxsZXQAAAAAABMAAAABAAAAAQ==",
            "AAAAAAAAAPtJbml0aWFsaXplIHRoZSBTREsgd2l0aCBPcmFjbGUncyBwdWJsaWMga2V5CgpUaGlzIG11c3QgYmUgY2FsbGVkIG9uY2UgYWZ0ZXIgZGVwbG95bWVudC4KVGhlIE9yYWNsZSBwdWJsaWMga2V5IGlzIGltbXV0YWJsZSBhZnRlciBpbml0aWFsaXphdGlvbi4KCiMgQXJndW1lbnRzCiogYG9yYWNsZV9wdWJrZXlgIC0gRWQyNTUxOSBwdWJsaWMga2V5IGZyb20gT3JhY2xlIHNlcnZpY2UKCiMgUGFuaWNzCiogSWYgYWxyZWFkeSBpbml0aWFsaXplZAAAAAAKaW5pdGlhbGl6ZQAAAAAAAQAAAAAAAAANb3JhY2xlX3B1YmtleQAAAAAAB9AAAAAJUHVibGljS2V5AAAAAAAAAA==",
            "AAAAAAAAAWtTdWJtaXQgc2lnbmVkIHJpc2sgc2NvcmUgZnJvbSBPcmFjbGUKCk9ubHkgdGhlIE9yYWNsZSBjYW4gY2FsbCB0aGlzICh2ZXJpZmllZCBieSBzaWduYXR1cmUpLgpVcGRhdGVzIHRoZSBvbi1jaGFpbiByaXNrIHN0YXRlIGZvciBhIHdhbGxldC4KCiMgQXJndW1lbnRzCiogYHBheWxvYWRgIC0gUmlzayBkYXRhICh3YWxsZXQsIHNjb3JlLCB0aW1lc3RhbXApCiogYHNpZ25hdHVyZWAgLSBFZDI1NTE5IHNpZ25hdHVyZSBmcm9tIE9yYWNsZQoKIyBQYW5pY3MKKiBJZiBzaWduYXR1cmUgaXMgaW52YWxpZAoqIElmIHRpbWVzdGFtcCBpcyB0b28gb2xkICg+NSBtaW51dGVzKQoqIElmIHJpc2sgc2NvcmUgaXMgb3V0IG9mIHJhbmdlICgwLTEwMCkAAAAAC3N1Ym1pdF9yaXNrAAAAAAIAAAAAAAAAB3BheWxvYWQAAAAH0AAAAAtSaXNrUGF5bG9hZAAAAAAAAAAACXNpZ25hdHVyZQAAAAAAB9AAAAAJU2lnbmF0dXJlAAAAAAAAAA==",
            "AAAAAAAAAWRDaGVjayBwZXJtaXNzaW9uIGRlY2lzaW9uIGZvciBhIHdhbGxldCAoU0RLIGNvcmUgZnVuY3Rpb24pCgpUaGlzIGlzIHRoZSBtYWluIGZ1bmN0aW9uIGludGVncmF0aW5nIHByb3RvY29scyBjYWxsLgpSZXR1cm5zIHRoZSByaXNrIGRlY2lzaW9uIHdpdGhvdXQgZW5mb3JjaW5nIGl0LgoKIyBBcmd1bWVudHMKKiBgd2FsbGV0YCAtIEFkZHJlc3MgdG8gY2hlY2sKCiMgUmV0dXJucwoqIGBSaXNrRGVjaXNpb25gIC0gQWxsb3csIExpbWl0KGFtb3VudCksIG9yIEZyZWV6ZQoKIyBEZWZhdWx0IEJlaGF2aW9yCiogSWYgd2FsbGV0IGlzIHVua25vd24sIHJldHVybnMgYEFsbG93YCAoaW5ub2NlbnQgdW50aWwgcHJvdmVuIHJpc2t5KQAAABBjaGVja19wZXJtaXNzaW9uAAAAAQAAAAAAAAAGd2FsbGV0AAAAAAATAAAAAQAAB9AAAAAMUmlza0RlY2lzaW9u",
            "AAAAAAAAAKlHZXQgT3JhY2xlJ3MgcHVibGljIGtleSAocmVhZC1vbmx5KQoKUmV0dXJucyB0aGUgRWQyNTUxOSBwdWJsaWMga2V5IHVzZWQgdG8gdmVyaWZ5IE9yYWNsZSBzaWduYXR1cmVzLgoKIyBSZXR1cm5zCiogT3JhY2xlJ3MgcHVibGljIGtleQoKIyBQYW5pY3MKKiBJZiBTREsgbm90IGluaXRpYWxpemVkAAAAAAAAEWdldF9vcmFjbGVfcHVia2V5AAAAAAAAAAAAAAEAAAfQAAAACVB1YmxpY0tleQAAAA==",
            "AAAAAQAAADBDb21wbGV0ZSByaXNrIHN0YXRlIGZvciBhIHdhbGxldCBzdG9yZWQgb24tY2hhaW4AAAAAAAAACVJpc2tTdGF0ZQAAAAAAAAMAAAAlQ29tcHV0ZWQgZGVjaXNpb24gYmFzZWQgb24gcmlzayBzY29yZQAAAAAAAAhkZWNpc2lvbgAAB9AAAAAMUmlza0RlY2lzaW9uAAAAHVVuaXggdGltZXN0YW1wIG9mIGxhc3QgdXBkYXRlAAAAAAAADGxhc3RfdXBkYXRlZAAAAAYAAAAVUmlzayBzY29yZSBmcm9tIDAtMTAwAAAAAAAACnJpc2tfc2NvcmUAAAAAAAQ=",
            "AAAAAQAAAC1QYXlsb2FkIHNpZ25lZCBieSBPcmFjbGUgKHdoYXQgZ2V0cyB2ZXJpZmllZCkAAAAAAAAAAAAAC1Jpc2tQYXlsb2FkAAAAAAMAAAAVUmlzayBzY29yZSBmcm9tIDAtMTAwAAAAAAAACnJpc2tfc2NvcmUAAAAAAAQAAAAmVW5peCB0aW1lc3RhbXAgd2hlbiBPcmFjbGUgc2lnbmVkIHRoaXMAAAAAAAl0aW1lc3RhbXAAAAAAAAAGAAAAG1dhbGxldCBhZGRyZXNzIGJlaW5nIHNjb3JlZAAAAAAGd2FsbGV0AAAAAAAT",
            "AAAAAgAAADhEZWNpc2lvbiByZXR1cm5lZCB0byBwcm90b2NvbHMgYWJvdXQgd2hhdCBhY3Rpb24gdG8gdGFrZQAAAAAAAAAMUmlza0RlY2lzaW9uAAAAAwAAAAAAAAAlV2FsbGV0IGlzIHNhZmUgLSBhbGxvdyBhbGwgb3BlcmF0aW9ucwAAAAAAAAVBbGxvdwAAAAAAAAEAAAA0V2FsbGV0IGhhcyBtb2RlcmF0ZSByaXNrIC0gbGltaXQgdG8gc3BlY2lmaWVkIGFtb3VudAAAAAVMaW1pdAAAAAAAAAEAAAAEAAAAAAAAACtXYWxsZXQgaXMgaGlnaCByaXNrIC0gZnJlZXplIGFsbCBvcGVyYXRpb25zAAAAAAZGcmVlemUAAA=="]), options);
        this.options = options;
    }
    fromJSON = {
        get_risk: (this.txFromJSON),
        is_frozen: (this.txFromJSON),
        initialize: (this.txFromJSON),
        submit_risk: (this.txFromJSON),
        check_permission: (this.txFromJSON),
        get_oracle_pubkey: (this.txFromJSON)
    };
}
