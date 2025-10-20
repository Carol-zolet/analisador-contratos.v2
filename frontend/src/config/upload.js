// Frontend upload configuration: keep in sync with backend ALLOWED_EXTS
export const ACCEPT_EXTS = ['.pdf', '.docx'];
export const ACCEPT_MIMES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
];
export const ACCEPT_LABEL = ACCEPT_EXTS.map((e) => e.replace('.', '').toUpperCase()).join(', ');
