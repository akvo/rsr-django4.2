import React from 'react'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'

const ConditionalLink = connect(({ userRdr: { lang, organisations } }) => ({ lang, organisations }))(({ record, children, lang, organisations, isProgram }) => {
  if(record.restricted === true){
    return <a href={`/en/project/${record.id}/`} target="_blank" rel="noopener noreferrer">{children}</a>
  }
  if (record.status === 'unpublished' && record.editable) {
    return (
      <Link to={`/${(isProgram || record.isProgram) ? 'programs' : 'projects'}/${record.id}`}>
        {children}
      </Link>
    )
  }
  if(record.isProgram) return <Link to={`/programs/${record.id}`}>{children}</Link>
  return (<Link to={`/projects/${record.id}/results`}>{children}</Link>)
})

export default ConditionalLink
