// Create a Text parameter named DataFolder that points to folder2/data.
// Duplicate this query and change FileName for each generated CSV.
let
    FileName = "monthly_revenue.csv",
    Source = Csv.Document(
        File.Contents(DataFolder & "\\" & FileName),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(
        Headers,
        {{"month", type date}, {"revenue_brl", Currency.Type}, {"delivered_orders", Int64.Type}}
    )
in
    Typed
