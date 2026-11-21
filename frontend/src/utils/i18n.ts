export type LanguageCode = 'auto' | 'hi-IN' | 'en-IN' | 'kn-IN' | 'te-IN';

export interface TranslationStrings {
  voiceLedger: string;
  statusLive: string;
  statusOffline: string;
  customers: string;
  settings: string;
  manualEntry: string;
  devPanel: string;
  
  // Dashboard Metrics
  todayCredit: string;
  givenToCustomers: string;
  todayPayment: string;
  collectedPayment: string;

  // Entry Cards
  udhaar: string;
  jama: string;
  recentLedgerEntries: string;
  latestOnTop: string;
  cleanKhata: string;
  emptyKhataHint: string;

  // Mic and States
  listening: string;
  thinking: string;
  speaking: string;
  heard: string;
  holdMicPrompt: string;
  listeningFeedback: string;
  holdOrTapToSpeak: string;
  recordingRelease: string;
  handsFree: string;

  // Errors & Fallbacks
  voiceNotUnderstood: string;
}

export const translations: Record<LanguageCode, TranslationStrings> = {
  'auto': {
    voiceLedger: 'VOICE LEDGER',
    statusLive: 'LIVE',
    statusOffline: 'OFFLINE',
    customers: 'Customers',
    settings: 'Settings',
    manualEntry: 'Manual Entry',
    devPanel: 'Dev Panel',

    todayCredit: 'Aaj Ka Udhaar',
    givenToCustomers: 'Given to customers',
    todayPayment: 'Aaj Ka Jama',
    collectedPayment: 'Collected payment',

    udhaar: 'UDHAAR',
    jama: 'JAMA',
    recentLedgerEntries: 'RECENT LEDGER ENTRIES',
    latestOnTop: 'Latest on top',
    cleanKhata: 'Khata is clean for today',
    emptyKhataHint: 'Hold mic below and say e.g. "Ramesh ka 340 udhaar"',

    listening: 'LISTENING',
    thinking: 'THINKING',
    speaking: 'SPEAKING',
    heard: 'HEARD',
    holdMicPrompt: 'Hold mic below to speak entry...',
    listeningFeedback: 'Suniye, bol rahe hain...',
    holdOrTapToSpeak: 'Hold or tap to speak',
    recordingRelease: 'Recording... (release or tap)',
    handsFree: 'HANDS-FREE',

    voiceNotUnderstood: 'Awaaz samajh nahi aayi. Phir se boliye.',
  },

  'hi-IN': {
    voiceLedger: 'वॉइस खाता (VOICE LEDGER)',
    statusLive: 'लाइव',
    statusOffline: 'ऑफलाइन',
    customers: 'ग्राहक सूची',
    settings: 'सेटिंग्स',
    manualEntry: 'मैन्युअल एंट्री',
    devPanel: 'डेव पैनल',

    todayCredit: 'आज का उधार',
    givenToCustomers: 'ग्राहकों को दिया',
    todayPayment: 'आज का जमा',
    collectedPayment: 'वसूल की गई राशि',

    udhaar: 'उधार (UDHAAR)',
    jama: 'जमा (JAMA)',
    recentLedgerEntries: 'ताज़ा खाता प्रविष्टियां',
    latestOnTop: 'नया सबसे ऊपर',
    cleanKhata: 'आज का खाता साफ है',
    emptyKhataHint: 'नीचे बटन दबाकर बोलें, जैसे "रमेश का 340 उधार"',

    listening: 'सुन रहे हैं',
    thinking: 'सोच रहे हैं',
    speaking: 'बोल रहे हैं',
    heard: 'सुना गया',
    holdMicPrompt: 'खाता लिखने के लिए नीचे माइक दबाएं...',
    listeningFeedback: 'सुन रहे हैं, बोलिए...',
    holdOrTapToSpeak: 'बोलने के लिए दबाएं या टैप करें',
    recordingRelease: 'रिकॉर्डिंग जारी है... (छोड़ें या टैप करें)',
    handsFree: 'हैंड्स-फ्री',

    voiceNotUnderstood: 'आवाज़ समझ नहीं आई। कृपया फिर से बोलिए।',
  },

  'te-IN': {
    voiceLedger: 'వాయిస్ ఖాతా (VOICE LEDGER)',
    statusLive: 'లైవ్',
    statusOffline: 'ఆఫ్‌లైన్',
    customers: 'కస్టమర్ల జాబితా',
    settings: 'సెట్టింగ్స్',
    manualEntry: 'మాన్యువల్ ఎంట్రీ',
    devPanel: 'డెవ్ ప్యానెల్',

    todayCredit: 'ఈరోజు అప్పు (UDHAAR)',
    givenToCustomers: 'కస్టమర్లకు ఇచ్చిన అప్పు',
    todayPayment: 'ఈరోజు జమ (JAMA)',
    collectedPayment: 'వసూలు చేసిన మొత్తం',

    udhaar: 'అప్పు (UDHAAR)',
    jama: 'జమ (JAMA)',
    recentLedgerEntries: 'ఇటీవలి ఖాతా ఎంట్రీలు',
    latestOnTop: 'తాజాది పైన',
    cleanKhata: 'ఈరోజు ఖాతా క్లియర్ గా ఉంది',
    emptyKhataHint: 'క్రింద మైక్ పట్టుకుని మాట్లాడండి, ఉదా: "రమేష్ కి 340 అప్పు"',

    listening: 'వింటున్నాము',
    thinking: 'ఆలోచిస్తున్నాము',
    speaking: 'మాట్లాడుతున్నాము',
    heard: 'విన్నది',
    holdMicPrompt: 'ఎంట్రీ రాయడానికి క్రింద మైక్ పట్టుకోండి...',
    listeningFeedback: 'వింటున్నాము, మాట్లాడండి...',
    holdOrTapToSpeak: 'మాట్లాడటానికి పట్టుకోండి లేదా ట్యాప్ చేయండి',
    recordingRelease: 'రికార్డింగ్ అవుతోంది... (వదిలేయండి)',
    handsFree: 'హ్యాండ్స్-ఫ్రీ',

    voiceNotUnderstood: 'వాయిస్ అర్థం కాలేదు. దయచేసి మళ్లీ చెప్పండి.',
  },

  'kn-IN': {
    voiceLedger: 'ಧ್ವನಿ ಖಾತೆ (VOICE LEDGER)',
    statusLive: 'ಲೈವ್',
    statusOffline: 'ಆಫ್‌ಲೈನ್',
    customers: 'ಗ್ರಾಹಕರ ಪಟ್ಟಿ',
    settings: 'ಸೆಟ್ಟಿಂಗ್ಸ್',
    manualEntry: 'ಮ್ಯಾನ್ಯುವಲ್ ಎಂಟ್ರಿ',
    devPanel: 'ಡೆವ್ ಪ್ಯಾನೆಲ್',

    todayCredit: 'ಇವತ್ತಿನ ಸಾಲ (UDHAAR)',
    givenToCustomers: 'ಗ್ರಾಹಕರಿಗೆ ನೀಡಿದ ಸಾಲ',
    todayPayment: 'ಇವತ್ತಿನ ಜಮಾ (JAMA)',
    collectedPayment: 'ವಸೂಲಾದ ಹಣ',

    udhaar: 'ಸಾಲ (UDHAAR)',
    jama: 'ಜಮಾ (JAMA)',
    recentLedgerEntries: 'ಇತ್ತೀಚಿನ ಖಾತಾ ನಮೂದುಗಳು',
    latestOnTop: 'ಇತ್ತೀಚಿನದ್ದು ಮೇಲೆ',
    cleanKhata: 'ಇವತ್ತಿನ ಖಾತೆ ಖಾಲಿ ಇದೆ',
    emptyKhataHint: 'ಕೆಳಗಿನ ಮೈಕ್ ಒತ್ತಿ ಹಿಡಿದು ಹೇಳಿ, ಉದಾ: "ರಮೇಶ್ ಗೆ 340 ಸಾಲ"',

    listening: 'ಕೇಳುತ್ತಿದ್ದೇವೆ',
    thinking: 'ಲೆಕ್ಕ ಹಾಕುತ್ತಿದ್ದೇವೆ',
    speaking: 'ಹೇಳುತ್ತಿದ್ದೇವೆ',
    heard: 'ಕೇಳಿಸಿಕೊಂಡಿದ್ದು',
    holdMicPrompt: 'ಖಾತೆ ಬರೆಯಲು ಕೆಳಗಿನ ಮೈಕ್ ಒತ್ತಿ ಹಿಡಿಯಿರಿ...',
    listeningFeedback: 'ಕೇಳಿಸಿಕೊಳ್ಳುತ್ತಿದ್ದೇವೆ, ಹೇಳಿ...',
    holdOrTapToSpeak: 'ಹೇಳಲು ಒತ್ತಿ ಹಿಡಿಯಿರಿ ಅಥವಾ ಟ್ಯಾಪ್ ಮಾಡಿ',
    recordingRelease: 'ರೆಕಾರ್ಡಿಂಗ್ ಆಗುತ್ತಿದೆ... (ಬಿಡಿ ಅಥವಾ ಟ್ಯಾಪ್ ಮಾಡಿ)',
    handsFree: 'ಹ್ಯಾಂಡ್ಸ್-ಫ್ರೀ',

    voiceNotUnderstood: 'ಧ್ವನಿ ಸ್ಪಷ್ಟವಾಗಿ ಕೇಳಿಸಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೊಮ್ಮೆ ಹೇಳಿ.',
  },

  'en-IN': {
    voiceLedger: 'VOICE LEDGER',
    statusLive: 'LIVE',
    statusOffline: 'OFFLINE',
    customers: 'Customers',
    settings: 'Settings',
    manualEntry: 'Manual Entry',
    devPanel: 'Dev Panel',

    todayCredit: "Today's Credit (Udhaar)",
    givenToCustomers: 'Given to customers',
    todayPayment: "Today's Payment (Jama)",
    collectedPayment: 'Collected payment',

    udhaar: 'CREDIT (UDHAAR)',
    jama: 'PAYMENT (JAMA)',
    recentLedgerEntries: 'RECENT LEDGER ENTRIES',
    latestOnTop: 'Latest on top',
    cleanKhata: 'Khata is clean for today',
    emptyKhataHint: 'Hold mic below and speak, e.g. "Ramesh 340 credit"',

    listening: 'LISTENING',
    thinking: 'THINKING',
    speaking: 'SPEAKING',
    heard: 'HEARD',
    holdMicPrompt: 'Hold mic below to speak entry...',
    listeningFeedback: 'Listening, please speak...',
    holdOrTapToSpeak: 'Hold or tap to speak',
    recordingRelease: 'Recording... (release or tap)',
    handsFree: 'HANDS-FREE',

    voiceNotUnderstood: 'Could not understand audio. Please speak again.',
  },
};

export function getTranslation(key: keyof TranslationStrings, lang?: string): string {
  const code = (lang || 'auto') as LanguageCode;
  const dict = translations[code] || translations['auto'];
  return dict[key] || translations['auto'][key];
}
