function formatJoiningDate(isoDate) {
  if (!isoDate) return "N/A";
  const parsed = new Date(`${isoDate}T00:00:00`);
  if (Number.isNaN(parsed.getTime())) return isoDate;
  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(parsed);
}


export function EmployeeCard({ employee }) {
  return (
    <article className="employee-card">
      <div className="card-top">
        <div>
          <h2 className="employee-name">{employee.name}</h2>
          <p className="employee-designation">{employee.designation}</p>
        </div>
        <span className="dept-tag">{employee.department}</span>
      </div>

      <dl className="card-details">
        <div className="detail-row">
          <dt>Email</dt>
          <dd>
            <a href={`mailto:${employee.email}`} className="email-link">
              {employee.email}
            </a>
          </dd>
        </div>
        <div className="detail-row">
          <dt>Joined</dt>
          <dd>{formatJoiningDate(employee.date_of_joining)}</dd>
        </div>
        <div className="detail-row">
          <dt>ID</dt>
          <dd>#{employee.id}</dd>
        </div>
      </dl>
    </article>
  );
}
