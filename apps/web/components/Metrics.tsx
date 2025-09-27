export default function Metrics({title, value, trend}:{title:string,value:string,trend:string}){
  return (
    <div>
      <div className="text-sm opacity-70">{title}</div>
      <div className="text-3xl font-bold">{value}</div>
      <div className="text-xs opacity-60 mt-1">{trend}</div>
    </div>
  )
}
