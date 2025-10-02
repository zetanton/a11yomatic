import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface PDFDocument {
  id: string;
  filename: string;
  file_size: number;
  upload_date: string;
  processing_status: string;
}

interface PDFState {
  documents: PDFDocument[];
  selectedPdf: string | null;
  uploadProgress: number;
  isUploading: boolean;
}

const initialState: PDFState = {
  documents: [],
  selectedPdf: null,
  uploadProgress: 0,
  isUploading: false,
};

const pdfSlice = createSlice({
  name: 'pdfs',
  initialState,
  reducers: {
    setDocuments: (state, action: PayloadAction<PDFDocument[]>) => {
      state.documents = action.payload;
    },
    addDocument: (state, action: PayloadAction<PDFDocument>) => {
      state.documents.unshift(action.payload);
    },
    removeDocument: (state, action: PayloadAction<string>) => {
      state.documents = state.documents.filter(
        (doc) => doc.id !== action.payload
      );
    },
    setSelectedPdf: (state, action: PayloadAction<string | null>) => {
      state.selectedPdf = action.payload;
    },
    setUploadProgress: (state, action: PayloadAction<number>) => {
      state.uploadProgress = action.payload;
    },
    setIsUploading: (state, action: PayloadAction<boolean>) => {
      state.isUploading = action.payload;
    },
  },
});

export const {
  setDocuments,
  addDocument,
  removeDocument,
  setSelectedPdf,
  setUploadProgress,
  setIsUploading,
} = pdfSlice.actions;

export default pdfSlice.reducer;


