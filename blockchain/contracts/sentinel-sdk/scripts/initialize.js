#!/usr/bin/env node

/**
 * Production Contract Initialization - FIXED IMPORTS
 * Using correct rpc module path from Stellar SDK v14.4.3
 */

import * as StellarSdk from '@stellar/stellar-sdk';

// Configuration
const CONTRACT_ID = 'CBH4H6ODNCQZGS5WQPPSGWKTKJKE5XCKFC4DRMTLMYTM2ZS43XK2SS3W';
const RPC_URL = 'https://soroban-testnet.stellar.org';
const NETWORK_PASSPHRASE = StellarSdk.Networks.TESTNET;
const ORACLE_PUBKEY_HEX = '93ebb785b8c8427ec32844881316e0463ad22438d8153a9f0cdb0b4c376d923c';
const SECRET_KEY = 'SCMPIRZGVMSCZNVVHT4OBOUSX5OT2BTKDVJZ2YB6PWZBR66QAAWHROZD';

async function initializeContract() {
    console.log('Production Contract Initialization');
    console.log('='.repeat(60));

    try {
        // 1. Load deployer keypair
        console.log('\n[1/6] Loading deployer keypair...');
        const keypair = StellarSdk.Keypair.fromSecret(SECRET_KEY);
        console.log(`   Deployer: ${keypair.publicKey()}`);

        // 2. Prepare Oracle public key
        console.log('\n[2/6] Preparing Oracle public key...');
        const oracleKeyBuffer = Buffer.from(ORACLE_PUBKEY_HEX, 'hex');
        console.log(`   Oracle Key: ${ORACLE_PUBKEY_HEX}`);
        console.log(`   Length: ${oracleKeyBuffer.length} bytes`);

        if (oracleKeyBuffer.length !== 32) {
            throw new Error('Invalid public key length');
        }

        // 3. Create ScVal parameter
        console.log('\n[3/6] Encoding as ScVal...');
        const param = StellarSdk.xdr.ScVal.scvBytes(oracleKeyBuffer);

        // 4. Connect to RPC - FIXED: use sdk.rpc not sdk.SorobanRpc
        console.log('\n[4/6] Connecting to Soroban RPC...');
        const server = new StellarSdk.rpc.Server(RPC_URL);
        const account = await server.getAccount(keypair.publicKey());
        console.log(`   Account sequence: ${account.sequenceNumber()}`);

        // 5. Build and simulate transaction
        console.log('\n[5/6] Building transaction...');
        const contract = new StellarSdk.Contract(CONTRACT_ID);

        const tx = new StellarSdk.TransactionBuilder(account, {
            fee: StellarSdk.BASE_FEE,
            networkPassphrase: NETWORK_PASSPHRASE,
        })
            .addOperation(contract.call('initialize', param))
            .setTimeout(30)
            .build();

        console.log('   Simulating...');
        const simulated = await server.simulateTransaction(tx);

        if (StellarSdk.rpc.Api.isSimulationError(simulated)) {
            console.error('   Simulation failed:', simulated);
            throw new Error('Transaction simulation failed');
        }

        console.log('   Simulation successful!');

        // Prepare and sign
        const prepared = StellarSdk.rpc.assembleTransaction(tx, simulated).build();
        prepared.sign(keypair);

        // 6. Submit transaction
        console.log('\n[6/6] Submitting transaction...');
        const result = await server.sendTransaction(prepared);
        console.log(`   TX Hash: ${result.hash}`);

        // Wait for confirmation
        console.log('   Waiting for confirmation...');
        let status = await server.getTransaction(result.hash);

        while (status.status === 'NOT_FOUND' || status.status === 'PENDING') {
            await new Promise(resolve => setTimeout(resolve, 1000));
            status = await server.getTransaction(result.hash);
        }

        if (status.status === 'SUCCESS') {
            console.log('\n' + '='.repeat(60));
            console.log('SUCCESS - Contract Initialized!');
            console.log('='.repeat(60));
            console.log(`\nContract ID: ${CONTRACT_ID}`);
            console.log(`Oracle Key:  ${ORACLE_PUBKEY_HEX}`);
            console.log(`TX Hash:     ${result.hash}`);
            console.log(`\nExplorer: https://stellar.expert/explorer/testnet/tx/${result.hash}`);
            console.log('\nContract ready for Oracle submissions!');
            process.exit(0);
        } else {
            throw new Error(`Transaction failed: ${status.status}`);
        }

    } catch (error) {
        console.error('\nError:', error.message);
        if (error.stack) console.error(error.stack);
        process.exit(1);
    }
}

initializeContract();
