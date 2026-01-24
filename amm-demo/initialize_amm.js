/**
 * Initialize AMM Contract
 * Links the AMM to the Sentinel Risk Engine
 */

import * as StellarSdk from '@stellar/stellar-sdk';

// Configuration
const AMM_ID = 'CCIB5TDDRURTQ5E4OHYZ7ONVSYNAC23FIYTCYLD3GOKASCRXFW2IPIRB';
const SENTINEL_ID = 'CBH4H6ODNCQZGS5WQPPSGWKTKJKE5XCKFC4DRMTLMYTM2ZS43XK2SS3W'; // V6
const RPC_URL = 'https://soroban-testnet.stellar.org';
const NETWORK_PASSPHRASE = StellarSdk.Networks.TESTNET;
const SECRET_KEY = 'SCMPIRZGVMSCZNVVHT4OBOUSX5OT2BTKDVJZ2YB6PWZBR66QAAWHROZD';

async function main() {
    console.log('Initializing AMM Contract...');

    const server = new StellarSdk.rpc.Server(RPC_URL);
    const keypair = StellarSdk.Keypair.fromSecret(SECRET_KEY);
    const account = await server.getAccount(keypair.publicKey());

    const contract = new StellarSdk.Contract(AMM_ID);

    // Create Address object for Sentinel ID
    const sentinelAddress = new StellarSdk.Address(SENTINEL_ID);

    const tx = new StellarSdk.TransactionBuilder(account, {
        fee: StellarSdk.BASE_FEE,
        networkPassphrase: NETWORK_PASSPHRASE,
    })
        .addOperation(contract.call('initialize',
            sentinelAddress.toScVal()
        ))
        .setTimeout(30)
        .build();

    const sim = await server.simulateTransaction(tx);
    if (StellarSdk.rpc.Api.isSimulationError(sim)) {
        console.error('Simulation failed:', sim);
        return;
    }

    console.log('Simulation success! Submitting...');
    const prepared = StellarSdk.rpc.assembleTransaction(tx, sim).build();
    prepared.sign(keypair);

    const result = await server.sendTransaction(prepared);
    console.log(`Success! TX: ${result.hash}`);
    console.log(`AMM ${AMM_ID} linked to Sentinel ${SENTINEL_ID}`);
}

main();
