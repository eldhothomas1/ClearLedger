import { useRef, useState, type ChangeEvent } from "react";
import { importTransactions } from "../api";

type Props = {
  onImported: (message: string) => void;
};

export default function ImportPanel({ onImported }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [fileName, setFileName] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  function chooseFile(event: ChangeEvent<HTMLInputElement>) {
    const nextFile = event.target.files?.[0] ?? null;
    setFile(nextFile);
    setFileName(nextFile?.name ?? "");
    setError("");
  }

  async function uploadFile() {
    if (!file) {
      setError("Choose a CSV file first.");
      return;
    }

    setUploading(true);
    setError("");

    try {
      const result = await importTransactions(file);
      const details = [
        `${result.imported} imported`,
        `${result.skipped_duplicates} duplicates skipped`,
      ];
      if (result.errors.length) details.push(`${result.errors.length} rows rejected`);
      onImported(details.join(", ") + ".");
      setFile(null);
      setFileName("");
      if (inputRef.current) inputRef.current.value = "";
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to import file");
    } finally {
      setUploading(false);
    }
  }

  return (
    <section className="panel import-panel" id="import">
      <div>
        <p className="eyebrow">CSV import</p>
        <h2>Upload a bank statement</h2>
        <p className="panel-copy">
          Use columns named date, merchant, amount, and optionally category.
        </p>
      </div>
      <div className="upload-controls">
        <input
          ref={inputRef}
          className="file-input"
          id="csv-file"
          type="file"
          accept=".csv,text/csv"
          onChange={chooseFile}
        />
        <label className="secondary-button file-label" htmlFor="csv-file">
          {fileName || "Choose CSV"}
        </label>
        <button className="primary-button" type="button" disabled={uploading} onClick={uploadFile}>
          {uploading ? "Importing..." : "Import file"}
        </button>
      </div>
      {error && <p className="form-error import-error">{error}</p>}
    </section>
  );
}
