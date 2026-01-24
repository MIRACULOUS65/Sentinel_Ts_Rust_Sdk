#!/usr/bin/env node

/**
 * Test Oracle Payload Submission - FIXED Address Encoding
 * Submit the signed payload from Oracle to contract for verification
 */

import * as StellarSdk from '@stellar/stellar-sdk';
import { readFileSync } from 'fs';

import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ORACLE_PATH = path.join(__dirname, '../../../../oracle/oracle_real_wallet.json');

const CONTRACT_ID = 'CBH4H6ODNCQZGS5WQPPSGWKTKJKE5XCKFC4DRMTLMYTM2ZS43XK2SS3W';
const RPC_URL = 'https://soroban-testnet.stellar.org';
const NETWORK_PASSPHRASE = StellarSdk.Networks.TESTNET;
const SECRET_KEY = 'SCMPIRZGVMSCZNVVHT4OBOUSX5OT2BTKDVJZ2YB6PWZBR66QAAWHROZD';

async function submitOraclePayload() {
    console.log('Testing Oracle Payload Submission');
    console.log('='.repeat(60));

    try {
        // 1. Load Oracle test output with REAL wallet
        console.log('\n[1/5] Loading Oracle-signed payload (real wallet)...');
        const oracleData = JSON.parse(readFileSync(ORACLE_PATH, 'utf8'));

        console.log('   Wallet:', oracleData.payload.wallet);
        console.log('   Risk Score:', oracleData.payload.risk_score);
        console.log('   Timestamp:', oracleData.payload.timestamp);
        console.log('   Signature:', oracleData.signature.substring(0, 32) + '...');

        // 2. Create RiskPayload ScVal with proper Address type
        console.log('\n[2/5] Encoding payload with Address type...');

        // Convert wallet string to Address
        const walletAddress = StellarSdk.Address.fromString(oracleData.payload.wallet);
        const walletScVal = walletAddress.toScVal();

        // Create RiskPayload struct: { wallet: Address, risk_score: u32, timestamp: u64 }
        // Struct fields in alphabetical order
        const payloadScVal = StellarSdk.xdr.ScVal.scvMap([
            new StellarSdk.xdr.ScMapEntry({
                key: StellarSdk.xdr.ScVal.scvSymbol('risk_score'),
                val: StellarSdk.nativeToScVal(oracleData.payload.risk_score, { type: 'u32' })
            }),
            new StellarSdk.xdr.ScMapEntry({
                key: StellarSdk.xdr.ScVal.scvSymbol('timestamp'),
                val: StellarSdk.nativeToScVal(oracleData.payload.timestamp, { type: 'u64' })
            }),
            new StellarSdk.xdr.ScMapEntry({
                key: StellarSdk.xdr.ScVal.scvSymbol('wallet'),
                val: walletScVal
            })
        ]);

        // 3. Create Signature ScVal (64 bytes)
        const signatureBuffer = Buffer.from(oracleData.signature, 'hex');
        const signatureScVal = StellarSdk.xdr.ScVal.scvBytes(signatureBuffer);

        console.log('   Payload struct created with Address');
        console.log('   Signature encoded (', signatureBuffer.length, 'bytes)');

        // 4. Build transaction
        console.log('\n[3/5] Building transaction...');
        const keypair = StellarSdk.Keypair.fromSecret(SECRET_KEY);
        const server = new StellarSdk.rpc.Server(RPC_URL);
        const account = await server.getAccount(keypair.publicKey());

        const contract = new StellarSdk.Contract(CONTRACT_ID);
        const tx = new StellarSdk.TransactionBuilder(account, {
            fee: StellarSdk.BASE_FEE,
            networkPassphrase: NETWORK_PASSPHRASE,
        })
            .addOperation(contract.call('submit_risk', payloadScVal, signatureScVal))
            .setTimeout(30)
            .build();

        // Simulate
        console.log('   Simulating...');
        const simulated = await server.simulateTransaction(tx);

        if (StellarSdk.rpc.Api.isSimulationError(simulated)) {
            console.error('   Simulation failed:');
            console.error('   Error:', simulated.error);
            throw new Error('Transaction simulation failed');
        }

        console.log('   Simulation successful!');

        // 5. Submit
        const prepared = StellarSdk.rpc.assembleTransaction(tx, simulated).build();
        prepared.sign(keypair);

        console.log('\n[4/5] Submitting transaction...');
        const result = await server.sendTransaction(prepared);
        console.log('   TX Hash:', result.hash);

        // Wait for confirmation
        console.log('\n[5/5] Waiting for confirmation...');
        let status = await server.getTransaction(result.hash);

        while (status.status === 'NOT_FOUND' || status.status === 'PENDING') {
            await new Promise(resolve => setTimeout(resolve, 1000));
            status = await server.getTransaction(result.hash);
        }

        if (status.status === 'SUCCESS') {
            console.log('\n' + '='.repeat(60));
            console.log('SUCCESS - Oracle Payload Accepted!');
            console.log('='.repeat(60));
            console.log('\nSignature verification PASSED!');
            console.log('Risk stored on-chain for wallet:', oracleData.payload.wallet);
            console.log('\nExplorer:', `https://stellar.expert/explorer/testnet/tx/${result.hash}`);
            console.log('\nContract now has risk data - ready for protocol integration!');
        } else {
            throw new Error(`Transaction failed: ${status.status}`);
        }

    } catch (error) {
        console.error('\nError:', error.message);
        if (error.stack) console.error(error.stack);
        process.exit(1);
    }
}

submitOraclePayload();
