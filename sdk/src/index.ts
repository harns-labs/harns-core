// clstr TypeScript SDK - main entry point.
import { Program, AnchorProvider, web3, BN } from "@coral-xyz/anchor";
import { PublicKey, Connection, Keypair, SystemProgram } from "@solana/web3.js";

export const PROGRAM_ID = new PublicKey("E1iTSqt1YkW6LoNXMspEoxsdotzEdmn3QjEJL5R3NUwe");
export const CLSTR_MINT = new PublicKey("5jBUVEcMCospWhpNnaePcUy8fnJ6L3FsrN2krdBSdVam");

export interface FlagAccountData {
  target: PublicKey;
  flagger: PublicKey;
  riskScore: BN;
  zkHash: number[];
  timestamp: BN;
  isActive: boolean;
}

export interface ConfigData {
  authority: PublicKey;
  bump: number;
  totalFlags: BN;
  totalBurns: BN;
}

export class ClstrClient {
  private program: Program;
  private provider: AnchorProvider;

  constructor(program: Program, provider: AnchorProvider) {
    this.program = program;
    this.provider = provider;
  }

  async initialize(): Promise<string> {
    const [configPda, bump] = PublicKey.findProgramAddressSync(
      [Buffer.from("config")],
      PROGRAM_ID
    );

    const tx = await this.program.methods
      .initialize(bump)
      .accounts({
        config: configPda,
        authority: this.provider.wallet.publicKey,
        systemProgram: SystemProgram.programId,
      })
      .rpc();

    return tx;
  }

  async flagWallet(
    target: PublicKey,
    riskScore: number,
    zkHash: number[]
  ): Promise<string> {
    const [configPda] = PublicKey.findProgramAddressSync(
      [Buffer.from("config")],
      PROGRAM_ID
    );

    const [flagPda] = PublicKey.findProgramAddressSync(
      [
        Buffer.from("flag"),
        target.toBuffer(),
        this.provider.wallet.publicKey.toBuffer(),
      ],
      PROGRAM_ID
    );

    const tx = await this.program.methods
      .flagWallet(new BN(riskScore), zkHash)
      .accounts({
        flagAccount: flagPda,
        config: configPda,
        target: target,
        flagger: this.provider.wallet.publicKey,
        systemProgram: SystemProgram.programId,
      })
      .rpc();

    return tx;
  }

  async burnFlag(target: PublicKey, flagger: PublicKey): Promise<string> {
    const [configPda] = PublicKey.findProgramAddressSync(
      [Buffer.from("config")],
      PROGRAM_ID
    );

    const [flagPda] = PublicKey.findProgramAddressSync(
      [Buffer.from("flag"), target.toBuffer(), flagger.toBuffer()],
      PROGRAM_ID
    );

    const tx = await this.program.methods
      .burnFlag()
      .accounts({
        flagAccount: flagPda,
        config: configPda,
        authority: this.provider.wallet.publicKey,
      })
      .rpc();

    return tx;
  }

  async getConfig(): Promise<ConfigData> {
    const [configPda] = PublicKey.findProgramAddressSync(
      [Buffer.from("config")],
      PROGRAM_ID
    );

    const account = await this.program.account.config.fetch(configPda);
    return account as unknown as ConfigData;
  }

  async getFlagAccount(
    target: PublicKey,
    flagger: PublicKey
  ): Promise<FlagAccountData> {
    const [flagPda] = PublicKey.findProgramAddressSync(
      [Buffer.from("flag"), target.toBuffer(), flagger.toBuffer()],
      PROGRAM_ID
    );

    const account = await this.program.account.flagAccount.fetch(flagPda);
    return account as unknown as FlagAccountData;
  }
}

export function deriveConfigPda(): PublicKey {
  const [pda] = PublicKey.findProgramAddressSync(
    [Buffer.from("config")],
    PROGRAM_ID
  );
  return pda;
}

export function deriveFlagPda(target: PublicKey, flagger: PublicKey): PublicKey {
  const [pda] = PublicKey.findProgramAddressSync(
    [Buffer.from("flag"), target.toBuffer(), flagger.toBuffer()],
    PROGRAM_ID
  );
  return pda;
}

// a8f15eda
