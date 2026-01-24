/**
 * Sentinel SDK Demo - AMM Integration
 * 
 * Demonstrates:
 * 1. Low Risk -> Swap Allowed
 * 2. Medium Risk -> Swap Limited
 * 3. High Risk -> Swap Frozen
 */

import * as StellarSdk from '@stellar/stellar-sdk';
import { execSync } from 'child_process';
import path from 'path';

const AMM_ID = 'CCIB5TDDRURTQ5E4OHYZ7ONVSYNAC23FIYTCYLD3GOKASCRXFW2IPIRB';
const RPC_URL = 'https://soroban-testnet.stellar.org';
const NETWORK_PASSPHRASE = StellarSdk.Networks.TESTNET;
const SECRET_KEY = 'SCMPIRZGVMSCZNVVHT4OBOUSX5OT2BTKDVJZ2YB6PWZBR66QAAWHROZD';
const TARGET_WALLET = 'GBGNKU6A27K5CITQQFIBA4EJZRXHF5PCDFDSL7T6JUTZ3LOONVM3QPXT';

// Paths
const UPDATE_RISK_SCRIPT = 'python update_risk.py'; // Assumes in same dir
const SUBMIT_RISK_SCRIPT = 'node ../blockchain/contracts/sentinel-sdk/scripts/test_submit_risk.js';

async function main() {
    console.log('='.repeat(60));
    console.log('SENTINEL SDK - END-TO-END DEMO');
    console.log('='.repeat(60));
    console.log(`AMM: ${AMM_ID}`);
    console.log(`User: ${TARGET_WALLET}`);

    const server = new StellarSdk.rpc.Server(RPC_URL);
    const keypair = StellarSdk.Keypair.fromSecret(SECRET_KEY);
    const account = await server.getAccount(keypair.publicKey());

    // Helper: Execute AMM Swap
    const attemptSwap = async (amount) => {
        process.stdout.write(`   Attempting swap of ${amount} tokens... `);
        try {
            const contract = new StellarSdk.Contract(AMM_ID);
            const tx = new StellarSdk.TransactionBuilder(account, { fee: StellarSdk.BASE_FEE, networkPassphrase: NETWORK_PASSPHRASE })
                .addOperation(contract.call('swap',
                    new StellarSdk.Address(TARGET_WALLET).toScVal(),
                    StellarSdk.nativeToScVal(amount, { type: 'i128' })
                ))
                .setTimeout(30)
                .build();

            const sim = await server.simulateTransaction(tx);
            if (StellarSdk.rpc.Api.isSimulationError(sim)) {
                console.log(`❌ BLOCKED`);
                // Extract error
                if (sim.error.includes("Amount exceeds risk limit")) return "LIMIT";
                if (sim.error.includes("Account is frozen")) return "FROZEN";
                return "FAIL";
            }
            console.log(`✅ SUCCESS`);
            return "SUCCESS";
        } catch (e) {
            console.log(`❌ ERROR: ${e.message}`);
            return "ERROR";
        }
    };

    // Helper: Update Risk Scenario
    const setRiskScenario = (score, label) => {
        console.log(`\n--- Scenario: ${label} (Score: ${score}) ---`);
        console.log(`[1] AI/ML Service detects risk level...`);
        console.log(`[2] Oracle signs risk payload...`);
        execSync(`${UPDATE_RISK_SCRIPT} ${score}`, { stdio: 'pipe' });

        console.log(`[3] Submitting to Sentinel Contract...`);
        // We suppress output unless error to keep demo clean
        try {
            execSync(SUBMIT_RISK_SCRIPT, { stdio: 'pipe' });
            console.log(`   Risk updated on-chain!`);
        } catch (e) {
            console.log(`   Error submitting risk!`);
        }
    };

    // --- EXECUTE SCENARIOS ---

    // Scenario 1: Clean Wallet
    setRiskScenario(0, "Safe User");
    await attemptSwap(100);  // Should succeed

    // Scenario 2: Medium Risk
    setRiskScenario(65, "Suspicious User");
    await attemptSwap(100);   // Should succeed (Under 5000 limit)
    await attemptSwap(10000); // Should fail (Over 5000 limit)

    // Scenario 3: High Risk
    setRiskScenario(95, "Malicious User");
    await attemptSwap(10);    // Should fail (Frozen)

    console.log('\n' + '='.repeat(60));
    console.log('DEMO COMPLETE');
}

main();
