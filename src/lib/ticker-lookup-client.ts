import { auth } from './firebase';

const LOOKUP_SYMBOL_FUNCTION_URL = 'https://lookup-symbol-32rtfol3iq-uc.a.run.app';

export interface LookupSymbolResponse {
  success: boolean;
  ticker: string;
  company_name: string;
}

export class TickerLookupClient {
  private static instance: TickerLookupClient;

  private constructor() {}

  static getInstance(): TickerLookupClient {
    if (!TickerLookupClient.instance) {
      TickerLookupClient.instance = new TickerLookupClient();
    }
    return TickerLookupClient.instance;
  }

  private async getAuthToken(): Promise<string> {
    const user = auth.currentUser;
    if (!user) {
      throw new Error('User not authenticated');
    }
    return await user.getIdToken();
  }

  async lookupSymbol(ticker: string): Promise<string | null> {
    const token = await this.getAuthToken();
    const response = await fetch(LOOKUP_SYMBOL_FUNCTION_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ ticker })
    });
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || 'Failed to lookup symbol');
    }

    const result = data as LookupSymbolResponse;
    return result.company_name || null;
  }
}

export const tickerLookupClient = TickerLookupClient.getInstance();
