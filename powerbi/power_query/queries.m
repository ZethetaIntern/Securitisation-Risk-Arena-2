let
    Source = Csv.Document(File.Contents("C:\path\to\data\raw\loans.csv"),[Delimiter=",", Columns=20, Encoding=1252, QuoteStyle=QuoteStyle.None]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedType = Table.TransformColumnTypes(PromotedHeaders,{{"loan_id", type text}, {"original_principal", type number}, {"interest_rate", type number}, {"origination_date", type date}})
in
    ChangedType
