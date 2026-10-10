import { useEffect, useRef, useState } from 'react'
import TransactionForm from '../components/TransactionForm.jsx'
import TransactionNavigation from '../components/TransactionNavigation.jsx'
import { transactionService } from '../services/transactionService.js'

const DRAFT_FIELD_LABELS = {
  transaction_type: 'transaction type',
  amount: 'amount',
  transaction_date: 'date',
  category_key: 'category',
  notes: 'notes',
}

const MAX_RECEIPT_BYTES = 10 * 1024 * 1024
const RECEIPT_MEDIA_TYPES = new Set(['image/jpeg', 'image/png', 'image/webp'])
const SPEECH_SESSION_MS = 60_000

function getSpeechRecognitionConstructor() {
  return globalThis.SpeechRecognition ?? globalThis.webkitSpeechRecognition ?? null
}

function speechErrorMessage(error) {
  if (error === 'not-allowed' || error === 'service-not-allowed') return 'Microphone permission was denied. You can type a description or use the manual form.'
  if (error === 'no-speech') return 'No speech was detected. Try again or type a description.'
  if (error === 'audio-capture') return 'No microphone is available. You can type a description or use the manual form.'
  return 'Speech recognition failed. You can try again, type a description, or use the manual form.'
}

function appendTranscript(existingText, transcript) {
  const addition = transcript.trim()
  if (!addition) return existingText
  const current = existingText.trimEnd()
  return current ? `${current}${/[.!?]$/.test(current) ? ' ' : '. '}${addition}` : addition
}

async function receiptFileError(file) {
  if (!file) return 'Choose one receipt image before creating a draft.'
  if (!RECEIPT_MEDIA_TYPES.has(file.type)) return 'Choose a JPEG, PNG, or WebP image.'
  if (file.size > MAX_RECEIPT_BYTES) return 'Choose an image that is 10 MB or smaller.'
  if (typeof globalThis.createImageBitmap === 'function') {
    try {
      const bitmap = await globalThis.createImageBitmap(file)
      bitmap.close()
    } catch {
      return 'This image is invalid or damaged. Choose a valid JPEG, PNG, or WebP image.'
    }
  }
  return ''
}

function AddTransactionPage() {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [fieldErrors, setFieldErrors] = useState({})
  const [pageError, setPageError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [successCount, setSuccessCount] = useState(0)
  const [describeOpen, setDescribeOpen] = useState(false)
  const [receiptOpen, setReceiptOpen] = useState(false)
  const [selectedReceipt, setSelectedReceipt] = useState(null)
  const [receiptError, setReceiptError] = useState('')
  const [receiptFieldError, setReceiptFieldError] = useState('')
  const [isCreatingReceiptDraft, setIsCreatingReceiptDraft] = useState(false)
  const [description, setDescription] = useState('')
  const [assistedError, setAssistedError] = useState('')
  const [assistedFieldError, setAssistedFieldError] = useState('')
  const [isCreatingDraft, setIsCreatingDraft] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [speechError, setSpeechError] = useState('')
  const [speechStatus, setSpeechStatus] = useState('')
  const [assistedDraft, setAssistedDraft] = useState(null)
  const [assistedDraftSource, setAssistedDraftSource] = useState(null)
  const submissionLock = useRef(false)
  const manualValuesRef = useRef(null)
  const recognitionRef = useRef(null)
  const speechTimerRef = useRef(null)
  const speechSupported = Boolean(getSpeechRecognitionConstructor())

  function finishListening() {
    setIsListening(false)
    if (speechTimerRef.current) {
      window.clearTimeout(speechTimerRef.current)
      speechTimerRef.current = null
    }
  }

  function stopRecognition() {
    recognitionRef.current?.stop()
    finishListening()
  }

  function startRecognition() {
    const SpeechRecognition = getSpeechRecognitionConstructor()
    if (!SpeechRecognition) {
      setSpeechError('Speech recognition is not available in this browser. You can type a description or use the manual form.')
      return
    }
    setSpeechError('')
    setSpeechStatus('')
    try {
      const recognition = new SpeechRecognition()
      recognition.lang = navigator.language || 'en-US'
      recognition.continuous = true
      recognition.interimResults = true
      recognition.onresult = (event) => {
        let finalTranscript = ''
        for (let index = event.resultIndex; index < event.results.length; index += 1) {
          const result = event.results[index]
          if (result.isFinal) finalTranscript += result[0]?.transcript ?? ''
        }
        if (finalTranscript) setDescription((current) => appendTranscript(current, finalTranscript))
      }
      recognition.onerror = (event) => {
        setSpeechError(speechErrorMessage(event.error))
        finishListening()
      }
      recognition.onend = () => {
        finishListening()
        setSpeechStatus('Speech recognition ended. Review or edit the text before creating a draft.')
      }
      recognitionRef.current = recognition
      recognition.start()
      setIsListening(true)
      speechTimerRef.current = window.setTimeout(() => {
        setSpeechError('The 60-second listening limit was reached. You can review the text, try again, or use the manual form.')
        recognition.stop()
        finishListening()
      }, SPEECH_SESSION_MS)
    } catch {
      recognitionRef.current = null
      finishListening()
      setSpeechError('Speech recognition could not start. Check microphone permission or type a description instead.')
    }
  }

  useEffect(() => () => {
    if (speechTimerRef.current) window.clearTimeout(speechTimerRef.current)
    recognitionRef.current?.abort?.()
  }, [])

  function hasManualValues(values = manualValuesRef.current) {
    if (!values) return false
    const parts = new Intl.DateTimeFormat('en', { timeZone: 'Europe/Madrid', year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(new Date())
    const dateParts = Object.fromEntries(parts.map(({ type, value }) => [type, value]))
    const today = `${dateParts.year}-${dateParts.month}-${dateParts.day}`
    return Boolean(
      values.amount || values.category_key || values.notes?.trim() || values.b_u_c ||
      values.reflective_context || values.transaction_type !== 'expense' ||
      (values.transaction_date && values.transaction_date !== today)
    )
  }

  function confirmReplacement() {
    return !hasManualValues() || window.confirm('Replace the values in the manual form with this draft?')
  }

  function handleManualValuesChange(values) {
    manualValuesRef.current = values
  }

  async function handleCreateDraft(event) {
    event.preventDefault()
    setAssistedError('')
    setAssistedFieldError('')
    if (!description.trim()) {
      setAssistedFieldError('Enter a transaction description.')
      return
    }
    if (description.length > 1000) {
      setAssistedFieldError('Use 1,000 characters or fewer.')
      return
    }
    if (!confirmReplacement()) return
    const manualValuesAtStart = JSON.stringify(manualValuesRef.current ?? null)

    setIsCreatingDraft(true)
    try {
      const response = await transactionService.createTextDraft(description)
      if (JSON.stringify(manualValuesRef.current ?? null) !== manualValuesAtStart && hasManualValues() && !window.confirm('Replace the values entered in the manual form while the draft was being created?')) return
      setAssistedDraft(response.data)
      setAssistedDraftSource('text')
      setFieldErrors({})
      setPageError('')
      setSuccessMessage('')
    } catch (requestError) {
      const message = requestError?.data?.error?.message || requestError.message
      setAssistedError(`${message || 'Unable to create a draft.'} Your text is still here, and you can enter the transaction manually.`)
    } finally {
      setIsCreatingDraft(false)
    }
  }

  async function handleCreateReceiptDraft(event) {
    event.preventDefault()
    setReceiptError('')
    const validationMessage = await receiptFileError(selectedReceipt)
    if (validationMessage) {
      setReceiptFieldError(validationMessage)
      return
    }
    setReceiptFieldError('')
    if (!confirmReplacement()) return
    const manualValuesAtStart = JSON.stringify(manualValuesRef.current ?? null)

    setIsCreatingReceiptDraft(true)
    try {
      const response = await transactionService.createReceiptDraft(selectedReceipt)
      if (JSON.stringify(manualValuesRef.current ?? null) !== manualValuesAtStart && hasManualValues() && !window.confirm('Replace the values entered in the manual form while the receipt draft was being created?')) return
      setAssistedDraft(response.data)
      setAssistedDraftSource('receipt')
      setFieldErrors({})
      setPageError('')
      setSuccessMessage('')
    } catch (requestError) {
      const message = requestError?.data?.error?.message || requestError.message
      setReceiptError(`${message || 'Unable to create a receipt draft.'} Your image is still selected, and you can enter the transaction manually.`)
    } finally {
      setIsCreatingReceiptDraft(false)
    }
  }

  function discardDraft() {
    setAssistedDraft(null)
    setAssistedDraftSource(null)
    manualValuesRef.current = null
    setFieldErrors({})
    setPageError('')
  }

  async function handleSubmit(transaction) {
    if (submissionLock.current) return
    submissionLock.current = true
    setIsSubmitting(true)
    setFieldErrors({})
    setPageError('')
    setSuccessMessage('')
    try {
      await transactionService.createTransaction(transaction)
      setSuccessMessage('Transaction saved. You can add another one.')
      setSuccessCount((count) => count + 1)
      setAssistedDraft(null)
      setAssistedDraftSource(null)
      manualValuesRef.current = null
    } catch (requestError) {
      const serverFields = requestError?.data?.error?.fields ?? {}
      const allowedFields = ['transaction_type', 'amount', 'transaction_date', 'category_key', 'notes', 'b_u_c', 'reflective_context']
      const errors = Object.fromEntries(Object.entries(serverFields).filter(([key]) => allowedFields.includes(key)))
      setFieldErrors(errors)
      if (Object.keys(serverFields).length === 0 || Object.keys(errors).length !== Object.keys(serverFields).length) {
        setPageError(requestError.message || 'Unable to save this transaction.')
      }
    } finally {
      submissionLock.current = false
      setIsSubmitting(false)
    }
  }

  return (
    <>
    <TransactionNavigation />
    <main className="container py-4">
      <div className="row justify-content-center">
        <div className="col-12 col-md-8 col-lg-6">
          <h1 className="mb-2">Add transaction</h1>
          <p className="text-secondary mb-4">Record one-time income or an expense. The date defaults to today.</p>

          <section className="card mb-4" aria-labelledby="describe-transaction-heading">
            <div className="card-body">
              <h2 className="h5 mb-0" id="describe-transaction-heading">
                <button
                  className="btn btn-link p-0 text-decoration-none"
                  type="button"
                  aria-expanded={describeOpen}
                  aria-controls="describe-transaction-panel"
                  onClick={() => setDescribeOpen((open) => !open)}
                >
                  Describe a transaction
                </button>
              </h2>
              {describeOpen && <div id="describe-transaction-panel" className="pt-3">
                <p className="text-secondary">For example, “I spent €12.50 on lunch today”. You can describe it in your own words.</p>
                <form onSubmit={handleCreateDraft}>
                  <label className="form-label" htmlFor="transaction-description">Transaction description</label>
                  {speechSupported && <div className="mb-2">
                    <button className="btn btn-outline-secondary" type="button" onClick={isListening ? stopRecognition : startRecognition} aria-pressed={isListening}>
                      {isListening ? 'Stop listening' : 'Start microphone'}
                    </button>
                    <span className="ms-2" role="status" aria-live="polite">{isListening ? 'Listening. Speak now; you can stop at any time.' : ''}</span>
                  </div>}
                  {speechStatus && <p className="form-text" role="status" aria-live="polite">{speechStatus}</p>}
                  {!speechSupported && <p className="form-text">Speech recognition is not available in this browser. You can type a description or use the manual form.</p>}
                  <p className="form-text">Browser/device speech recognition may use an external speech service, depending on its settings. The app does not record or retain audio.</p>
                  <textarea
                    className={`form-control${assistedFieldError ? ' is-invalid' : ''}`}
                    id="transaction-description"
                    rows="3"
                    maxLength={1000}
                    value={description}
                    onChange={(event) => { setDescription(event.target.value); setAssistedFieldError(''); setAssistedError(''); setSpeechError(''); setSpeechStatus('') }}
                    aria-invalid={Boolean(assistedFieldError)}
                    aria-describedby={assistedFieldError ? 'transaction-description-error transaction-description-count' : 'transaction-description-count'}
                  />
                  {speechError && <div className="alert alert-warning py-2" role="status" aria-live="polite">{speechError}</div>}
                  {assistedFieldError && <div className="invalid-feedback" id="transaction-description-error">{assistedFieldError}</div>}
                  <div id="transaction-description-count" className="form-text mb-3">{description.length}/1,000 characters</div>
                  {assistedError && <div className="alert alert-danger" role="alert">{assistedError}</div>}
                  <button className="btn btn-outline-primary" type="submit" disabled={isCreatingDraft}>
                    {isCreatingDraft ? 'Creating draft…' : 'Create draft'}
                  </button>
                </form>
              </div>}
            </div>
          </section>

          <section className="card mb-4" aria-labelledby="upload-receipt-heading">
            <div className="card-body">
              <h2 className="h5 mb-0" id="upload-receipt-heading">
                <button
                  className="btn btn-link p-0 text-decoration-none"
                  type="button"
                  aria-expanded={receiptOpen}
                  aria-controls="upload-receipt-panel"
                  onClick={() => setReceiptOpen((open) => !open)}
                >
                  Upload a receipt
                </button>
              </h2>
              {receiptOpen && <div id="upload-receipt-panel" className="pt-3">
                <p className="text-secondary">One JPEG, PNG, or WebP image up to 10 MB. The upload is processed only to prepare a draft and is not stored. Review the draft before saving.</p>
                <form onSubmit={handleCreateReceiptDraft}>
                  <label className="form-label" htmlFor="receipt-image">Receipt image</label>
                  <input
                    className={`form-control${receiptFieldError ? ' is-invalid' : ''}`}
                    id="receipt-image"
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    aria-invalid={Boolean(receiptFieldError)}
                    aria-describedby={receiptFieldError ? 'receipt-image-error receipt-image-feedback' : 'receipt-image-feedback'}
                    onChange={(event) => {
                      setSelectedReceipt(event.target.files?.[0] ?? null)
                      setReceiptFieldError('')
                      setReceiptError('')
                    }}
                  />
                  {receiptFieldError && <div className="invalid-feedback" id="receipt-image-error">{receiptFieldError}</div>}
                  <div id="receipt-image-feedback" className="form-text mb-3">
                    {selectedReceipt ? `Selected: ${selectedReceipt.name} (${(selectedReceipt.size / (1024 * 1024)).toFixed(2)} MB)` : 'No image selected.'}
                  </div>
                  {receiptError && <div className="alert alert-danger" role="alert">{receiptError}</div>}
                  <button className="btn btn-outline-primary" type="submit" disabled={isCreatingReceiptDraft}>
                    {isCreatingReceiptDraft ? 'Creating draft…' : 'Create draft'}
                  </button>
                </form>
              </div>}
            </div>
          </section>

          {assistedDraft && <div className="alert alert-info" role="status" aria-live="polite">
            <strong>Review before saving.</strong> {assistedDraftSource === 'receipt' ? 'This draft came from a receipt image. ' : ''}Check every field, fill any missing details, then save through the normal transaction form.
            {assistedDraft.missing_fields?.length > 0 && <p className="mb-1 mt-2">Needs your input: {assistedDraft.missing_fields.map((field) => DRAFT_FIELD_LABELS[field] ?? field).join(', ')}.</p>}
            {assistedDraft.uncertainties?.length > 0 && <ul className="mb-2 mt-2">
              {assistedDraft.uncertainties.map(({ field, reason }) => <li key={field}><strong>{DRAFT_FIELD_LABELS[field] ?? field}:</strong> {reason}</li>)}
            </ul>}
            <button className="btn btn-sm btn-outline-secondary mt-2" type="button" onClick={discardDraft} disabled={isSubmitting}>Discard draft</button>
          </div>}

          {successMessage && <div className="alert alert-success" role="status" aria-live="polite">{successMessage}</div>}
          {pageError && <div className="alert alert-danger" role="alert" aria-live="polite">{pageError}</div>}

          <TransactionForm
            key={assistedDraft ? 'assisted-draft' : 'manual-form'}
            onSubmit={handleSubmit}
            isSubmitting={isSubmitting}
            fieldErrors={fieldErrors}
            successCount={successCount}
            initialValues={assistedDraft ? {
              ...assistedDraft.draft,
              amount: assistedDraft.draft.amount ?? '',
              transaction_date: assistedDraft.draft.transaction_date ?? '',
              category_key: assistedDraft.draft.category_key ?? '',
              notes: assistedDraft.draft.notes ?? '',
              b_u_c: '',
              reflective_context: '',
            } : undefined}
            onValuesChange={handleManualValuesChange}
          />
        </div>
      </div>
    </main>
    </>
  )
}

export default AddTransactionPage
