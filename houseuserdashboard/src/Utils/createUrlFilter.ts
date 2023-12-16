export const createUrlFilter = (filterQuery: any): string => {
  const queryWithIncludeProperties: any = Object.entries(filterQuery).reduce(
    (e: any[], i: any[]) => {
      if (Array.isArray(i[1])) {
        i[1].forEach(f => {
          e.push([i[0], f]);
        });
      } else {
        e.push([i[0], i[1]]);
      }

      return e;
    },
    []
  );

  return new URLSearchParams(queryWithIncludeProperties).toString();
};
