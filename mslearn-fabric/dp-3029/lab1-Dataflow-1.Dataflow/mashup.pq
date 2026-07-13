[DefaultOutputDestinationSettings = [DestinationDefinition = [Kind = "Reference", QueryName = "DefaultDestination", IsNewTarget = true], UpdateMethod = [Kind = "Replace"], DestinationTypeSettings = [Kind = "Table"]], StagingDefinition = [Kind = "FastCopy"]]
section Section1;
[BindToDefaultDestination = true]
shared Store = let
  Source = Csv.Document(Web.Contents("https://raw.githubusercontent.com/MicrosoftLearning/mslearn-fabric/refs/heads/main/Allfiles/Labs/22a/Store.csv"), [Delimiter = "|", Columns = 7, Encoding = 1200, QuoteStyle = QuoteStyle.None]),
  #"Changed column type" = Table.TransformColumnTypes(Source, {{"Column1", Int64.Type}, {"Column2", type text}, {"Column3", Int64.Type}, {"Column4", type text}, {"Column5", type text}, {"Column6", type text}, {"Column7", type text}}),
  #"Rename columns" = Table.RenameColumns(#"Changed column type", {{"Column1", "BusinessEntityID"}, {"Column2", "Name"}, {"Column3", "SalesPersonID"}, {"Column4", "Demographics"}, {"Column5", "rowguid"}, {"Column6", "ModifiedDate"}}),
  colsToTrim = {"Name", "Demographics", "rowguid"},
  Result = Table.TransformColumns(
            #"Rename columns",
            List.Transform(
                colsToTrim,
                each {
                    _,
                    (t as text) => if Text.Length(t) > 0 then Text.Start(t, Text.Length(t) - 1) else t,
                    type text
                }
            )
        ),
  #"Remove columns" = Table.RemoveColumns(Result, {"rowguid", "Column7"}),
  #"Transform columns" = Table.TransformColumns(#"Remove columns", {{"Demographics", each Text.Replace(_, "﻿", ""), type text}}),
  AddXml = Table.AddColumn(#"Transform columns", "XML", each Xml.Tables([Demographics]), type table),
  ExpandXml = Table.ExpandTableColumn(AddXml, "XML", {"AnnualSales", "AnnualRevenue", "BankName", "BusinessType", "YearOpened", "Specialty", "SquareFeet", "Brands", "Internet", "NumberEmployees"}, {"AnnualSales", "AnnualRevenue", "BankName", "BusinessType", "YearOpened", "Specialty", "SquareFeet", "Brands", "Internet", "NumberEmployees"}),
  #"Remove columns 1" = Table.RemoveColumns(ExpandXml, {"Demographics"}),
  #"Transform columns 1" = Table.TransformColumns(#"Remove columns 1", {{"ModifiedDate", each Text.Start(_, Text.Length(_) - 1), type text}}),
  #"Change type" = Table.TransformColumnTypes(#"Transform columns 1", {{"ModifiedDate", type datetime}}),
  #"Change type 1" = Table.TransformColumnTypes(#"Change type", {{"AnnualSales", Int64.Type}, {"AnnualRevenue", Int64.Type}, {"SquareFeet", Int64.Type}, {"NumberEmployees", Int64.Type}}),
  #"Add column" = Table.AddColumn(#"Change type 1", "StoreSize", each if [SquareFeet] >= 0 and [SquareFeet] <= 10000 then "Small"
        else if [SquareFeet] >= 10001 and [SquareFeet] <= 40000 then "Medium"
        else if [SquareFeet] >= 40001 and [SquareFeet] <= 80000 then "Large"
        else null, type text),
  #"Change type 2" = Table.TransformColumnTypes(#"Add column", {{"Name", type text}, {"BankName", type text}, {"BusinessType", type text}, {"YearOpened", type text}, {"Specialty", type text}, {"Brands", type text}, {"Internet", type text}, {"StoreSize", type text}})
in
  #"Change type 2";
shared DefaultDestination = let
  Source = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false, HierarchicalNavigation = true, EnableVorder = true, OutputMetadataRefresh = true]),
  #"Navigation 1" = Source{[workspaceId = "191f9394-3785-4e15-b427-96135e136a7f"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[lakehouseId = "da9d64f5-6f97-42f1-843b-e8bebf438c5a"]}[Data],
  #"Navigation 3" = #"Navigation 2"{[Id = "dbo", ItemKind = "Schema"]}[Data]
in
  #"Navigation 3";
