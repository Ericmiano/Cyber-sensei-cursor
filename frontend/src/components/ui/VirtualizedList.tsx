import { ReactNode, useRef, useEffect, useState, memo } from "react";
import { cn } from "@/lib/utils";

interface VirtualizedListProps<T> {
  items: T[];
  height: number;
  itemHeight: number;
  renderItem: (item: T, index: number) => ReactNode;
  className?: string;
  overscanCount?: number;
}

export function VirtualizedList<T>({
  items,
  height,
  itemHeight,
  renderItem,
  className,
  overscanCount = 5,
}: VirtualizedListProps<T>) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [scrollTop, setScrollTop] = useState(0);

  const totalHeight = items.length * itemHeight;
  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscanCount);
  const endIndex = Math.min(
    items.length,
    Math.ceil((scrollTop + height) / itemHeight) + overscanCount
  );

  const visibleItems = items.slice(startIndex, endIndex);

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
  };

  return (
    <div
      ref={containerRef}
      className={cn("overflow-auto", className)}
      style={{ height }}
      onScroll={handleScroll}
    >
      <div style={{ height: totalHeight, position: "relative" }}>
        {visibleItems.map((item, index) => (
          <div
            key={startIndex + index}
            style={{
              position: "absolute",
              top: (startIndex + index) * itemHeight,
              height: itemHeight,
              width: "100%",
            }}
          >
            {renderItem(item, startIndex + index)}
          </div>
        ))}
      </div>
    </div>
  );
}

// Grid virtualization for achievements/modules
interface VirtualizedGridProps<T> {
  items: T[];
  height: number;
  itemHeight: number;
  columns: number;
  renderItem: (item: T, index: number) => ReactNode;
  className?: string;
  gap?: number;
}

export function VirtualizedGrid<T>({
  items,
  height,
  itemHeight,
  columns,
  renderItem,
  className,
  gap = 16,
}: VirtualizedGridProps<T>) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [scrollTop, setScrollTop] = useState(0);

  const rowCount = Math.ceil(items.length / columns);
  const rowHeight = itemHeight + gap;
  const totalHeight = rowCount * rowHeight;
  
  const startRowIndex = Math.max(0, Math.floor(scrollTop / rowHeight) - 2);
  const endRowIndex = Math.min(
    rowCount,
    Math.ceil((scrollTop + height) / rowHeight) + 2
  );

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
  };

  return (
    <div
      ref={containerRef}
      className={cn("overflow-auto", className)}
      style={{ height }}
      onScroll={handleScroll}
    >
      <div style={{ height: totalHeight, position: "relative" }}>
        {Array.from({ length: endRowIndex - startRowIndex }, (_, rowOffset) => {
          const rowIndex = startRowIndex + rowOffset;
          const startItemIndex = rowIndex * columns;
          const rowItems = items.slice(startItemIndex, startItemIndex + columns);
          
          return (
            <div
              key={rowIndex}
              style={{
                position: "absolute",
                top: rowIndex * rowHeight,
                height: itemHeight,
                width: "100%",
                display: "flex",
                gap,
                padding: "0 4px",
              }}
            >
              {rowItems.map((item, colIndex) => (
                <div key={startItemIndex + colIndex} style={{ flex: 1 }}>
                  {renderItem(item, startItemIndex + colIndex)}
                </div>
              ))}
              {/* Fill empty cells */}
              {rowItems.length < columns &&
                Array(columns - rowItems.length)
                  .fill(null)
                  .map((_, i) => <div key={`empty-${i}`} style={{ flex: 1 }} />)}
            </div>
          );
        })}
      </div>
    </div>
  );
}
