declare module 'node:crypto' {
  export function createHash(algorithm: string): {
    update(data: string | Buffer): { digest(encoding: 'hex'): string };
  };
  export function sign(algorithm: null, data: Buffer, key: string): Buffer;
  export function verify(algorithm: null, data: Buffer, key: string, signature: Buffer): boolean;
  export function generateKeyPairSync(type: 'ed25519'): {
    publicKey: { export(options: { type: 'spki'; format: 'pem' }): string | Buffer };
    privateKey: { export(options: { type: 'pkcs8'; format: 'pem' }): string | Buffer };
  };
}

declare const Buffer: {
  from(input: string, encoding?: string): Buffer;
};

declare interface Buffer {
  toString(encoding?: string): string;
}
