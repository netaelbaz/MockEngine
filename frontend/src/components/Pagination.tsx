interface PaginationProps {
  total: number
  pageSize: number
  page: number
  onPageChange: (page: number) => void
}

export function Pagination({ total, pageSize, page, onPageChange }: PaginationProps) {
  const totalPages = Math.ceil(total / pageSize)
  if (totalPages <= 1) return null

  return (
    <div className="flex items-center justify-between pt-4 border-t border-zinc-200 mt-2">
      <span className="text-sm text-zinc-500">
        {page * pageSize + 1}–{Math.min((page + 1) * pageSize, total)} of {total}
      </span>
      <div className="flex gap-2">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page === 0}
          className="px-3 py-1.5 rounded-lg border border-zinc-300 text-sm disabled:opacity-40 hover:bg-zinc-50"
        >
          Previous
        </button>
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page >= totalPages - 1}
          className="px-3 py-1.5 rounded-lg border border-zinc-300 text-sm disabled:opacity-40 hover:bg-zinc-50"
        >
          Next
        </button>
      </div>
    </div>
  )
}
