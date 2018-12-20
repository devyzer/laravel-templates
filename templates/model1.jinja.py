<?php

    namespace {{data['paths']['controller']}}\{{data['modelName']}};

    use {{data['paths']['controller']}}\Controller;
    use Illuminate\Http\Request;
    use \Illuminate\Http\Response;
    use {{data['paths']['createRequest']}}\{{data['modelName']}}\Create{{data['modelName']}};
    use {{data['paths']['updateRequest']}}\{{data['modelName']}}\Update{{data['modelName']}};
    use {{data['paths']['repository']}}\{{data['modelName']}}Repository;
    use Prettus\Repository\Criteria\RequestCriteria;
    //use XLabTechs\AdminListing\Facades\AdminListing;
    use {{data['paths']['model']}}\{{data['modelName']}};
    {% set models_names = [] %} {% call_names=[] %}
    {%for item in data['foreign'] %} {%if not data['in_array'](item['modelName'],models_names)  %}
    {% set models_names = data['array_push'](models_names,item['modelName']) %}
    {% endfor %}{% endif %}
@if(count($foreign))
    @foreach($foreign as $item1)
        @php
           if(!in_array($item1['modelName'],$models_names))
            array_push($models_names,$item1['modelName']);
        @endphp
        @endforeach
    @endif
    @php
        $mtm_model=false;
@endphp
@if(isset($relations['belongsTo'])&&count($relations['belongsTo']))
    @foreach($relations['belongsTo'] as $item1)
        @php
        if(!in_array($item1['related_model_name'],$models_names))
        array_push($models_names,$item1['related_model_name']);
        @endphp
    @endforeach
@endif
@if(isset($relations['belongsToMany'])&&count($relations['belongsToMany']))
    @foreach($relations['belongsToMany'] as $item)
          @php
            if(!in_array($item['related_model_name'],$models_names))
            array_push($models_names,$item['related_model_name']);
            if(!in_array($item['middleTableModel'],$models_names))
            array_push($models_names,$item['middleTableModel']);
          @endphp
    @endforeach
@endif
@foreach( $models_names as $item1)
    use App\Models\ {{ $item1 }};
@endforeach
class {{ $controllerBaseName }} extends Controller
{
/** @var {{$modelVariableName}}Repository */
private ${{$modelVariableName}}Repository;


public function __construct({{$modelWithNamespaceFromDefault}}Repository ${{$modelVariableName}}Repo)
{
$this->{{$modelVariableName}}Repository = ${{$modelVariableName}}Repo;
}


/**
* Display a listing of the {{$modelBaseName}}.
*
* {{'@'}}param  Request $request
* {{'@'}}return Response | \Illuminate\View\View|Response
*/

public function index(Request $request)
{
$this-> {{$modelVariableName}}Repository->pushCriteria(new RequestCriteria($request));
$data=$this-> {{$modelVariableName}}Repository
@if(count($relation_classes))
    ->with(@foreach($relation_classes as $key=>$item)@if($key==0)
        "{{$item}}"@else,"{{$item}}"@endif @endforeach{{")"}}
@endif
->paginate(25);
@if(isset($relations['belongsToMany'])&&count($relations['belongsToMany']))
    @php
        $weakness=[];
    @endphp
    @foreach($relations['belongsToMany'] as $item1)
        @if($item1['weakness'])
            ${{$item1['related_table']}} = [];
            foreach ($data as $item) {
            ${{$item1['related_table']}}[$item->id] = [];
            ${{$item1['middleTable']}} ={{$item1['middleTableModel']}}::where('{{$modelVariableName}}_id', '=', $item->id)->get();
            foreach (${{$item1['middleTable']}} as $object) {
            $temp = {{$item1['related_model_name']}}::where('id', '=', $object['{{$item1['related_class']}}_id'])->get();
            if (isset($temp[0]))
            array_push( ${{$item1['related_table']}}[$item['id']], $temp[0]);
            }
            }
            @php
                array_push($weakness, $item1['related_table']);
            @endphp
        @endif
    @endforeach
@endif

return view('backend.{{$tableName}}.index'@if(isset($weakness)&&count($weakness)),compact(
@foreach($weakness as $key=> $item1)
    @if($key==0)"{{$item1}}"@else ,"{{$item1}}" @endif
@endforeach{{")"}}
@endif{{")"}}->with('{{$tableName
                }}', $data);
}



@if(isset($relations['belongsTo'])&&count($relations['belongsTo'])))
/*
* one to many
*/
@foreach($relations['belongsTo'] as $item1)
    @php
             array_push($call_names,$item1['related_class']);
    @endphp
    public function {{$item1['related_class']}}(Request $request,$parent_id)
    {

    return view('backend.{{$tableName}}.index')->with('{{$tableName
            }}', $this-> {{$modelVariableName}}Repository
    @if(count($relation_classes))
        ->with(@foreach($relation_classes as $key=>$item)@if($key==0)
            "{{$item}}"@else,"{{$item}}"@endif @endforeach{{")"}}
    @endif
    ->getPaginated(25,['{{$item1['related_class']}}_id'=>$parent_id]));
    }
@endforeach
@endif

@if(isset($relations['belongsToMany'])&&count($relations['belongsToMany']))
    /*
    * many to many
    */
    @foreach( $relations['belongsToMany'] as $item1)

        @if (!in_array($item1['related_class'],$call_names))
            @php
                array_push($call_names,$item1['related_class']);
            @endphp
        public function {{$item1['related_class']}}(Request $request,$foriegn_id)
        {
        $this-> {{$modelVariableName}}Repository->pushCriteria(new RequestCriteria($request));
        $data=$this-> {{$modelVariableName}}Repository
        @if(count($relation_classes))
            ->with(@foreach($relation_classes as $key=>$item)@if($key==0)
                "{{$item}}"@else,"{{$item}}"@endif @endforeach{{")"}}
        @endif
        ->paginate(25);

        foreach ($data as $key => $items) {
        $temp2 = [];
        ${{$item1['middleTable']}} ={{$item1['middleTableModel']}}::where('{{$modelVariableName}}_id', '=', $items->id)->get();
        foreach (${{$item1['middleTable']}} as $item2) {
        array_push($temp2, $item2->{{$item1['related_class']}}_id);
        }
        if (!in_array($foriegn_id, $temp2)) {
        unset($data[$key]);
        }
        }

        $part=count($data);
        @if(isset($relations['belongsToMany'])&&count($relations['belongsToMany']))
            @php
                $weakness=[];
            @endphp
            @foreach($relations['belongsToMany'] as $item1)
                @if($item1['weakness'])
                    ${{$item1['related_table']}} = [];
                    foreach ($data as $item) {
                    ${{$item1['related_table']}}[$item->id] = [];
                    ${{$item1['middleTable']}} ={{$item1['middleTableModel']}}::where('{{$modelVariableName}}_id', '=', $item->id)->get()->toarray();
                    foreach (${{$item1['middleTable']}} as $object) {
                    $temp = {{$item1['related_model_name']}}::where('id', '=', $object['{{$item1['related_class']}}_id'])->get()->toarray();
                    if (isset($temp[0]))
                    array_push( ${{$item1['related_table']}}[$item['id']], $temp[0]);
                    }
                    }
                    @php
                        array_push($weakness, $item1['related_table']);
                    @endphp
                @endif
            @endforeach
        @endif

        return view('backend.{{$tableName}}.index'@if(isset($weakness)&&count($weakness)),compact(
        @foreach($weakness as $key=> $item1)
            @if($key==0)"{{$item1}}"@else ,"{{$item1}}" @endif
        @endforeach{{")"}}
        @endif{{")"}}->with(['{{$tableName
            }}'=> $data,'part'=>$part]);
        }

        @endif
    @endforeach
@endif

@foreach($foreign as $item1)

    @if (!in_array($item1['lowerModelName'],$call_names))
        @php
            array_push($call_names,$item1['lowerModelName']);
        @endphp
    public function {{$item1['lowerModelName']}}(Request $request,$parent_id)
    {
    $data=$this-> {{$modelVariableName}}Repository
    @if(count($relation_classes))
        ->with(@foreach($relation_classes as $key=>$item)@if($key==0)
            "{{$item}}"@else,"{{$item}}"@endif @endforeach{{")"}}
    @endif
    ->getPaginated(25,['{{$item1['field_name']}}'=>$parent_id]);

    @if(isset($relations['belongsToMany'])&&count($relations['belongsToMany']))
        @php
            $weakness=[];
        @endphp
        @foreach($relations['belongsToMany'] as $item1)
            @if($item1['weakness'])
                ${{$item1['related_table']}} = [];
                foreach ($data as $item) {
                ${{$item1['related_table']}}[$item->id] = [];
                ${{$item1['middleTable']}} ={{$item1['middleTableModel']}}::where('{{$modelVariableName}}_id', '=', $item->id)->get()->toarray();
                foreach (${{$item1['middleTable']}} as $object) {
                $temp = {{$item1['related_model_name']}}::where('id', '=', $object['{{$item1['related_class']}}_id'])->get()->toarray();
                if (isset($temp[0]))
                array_push( ${{$item1['related_table']}}[$item['id']], $temp[0]);
                }
                }
                @php
                    array_push($weakness, $item1['related_table']);
                @endphp
            @endif
        @endforeach
    @endif

    return view('backend.{{$tableName}}.index'@if(isset($weakness)&&count($weakness)),compact(
    @foreach($weakness as $key=> $item1)
        @if($key==0)"{{$item1}}"@else ,"{{$item1}}" @endif
    @endforeach{{")"}}
    @endif{{")"}}->with('{{$tableName
            }}',$data);
    }
@endif
@endforeach


/**
* Show the form for creating a new {{$modelBaseName}}.
*
* @return Response | \Illuminate\View\View|Response
*/
public function create()
{
@if(count($foreign))
    @foreach($foreign as $item1)
        ${{$item1['table']}} = {{$item1['modelName']}}::all();
        $selected{{$item1['modelName']}} = {{$item1['modelName']}}::first()?{{$item1['modelName']}}::first()->_id:0;
    @endforeach
@endif
@php
    $weakness=[];
  $select_data=[];
@endphp
@if(isset($relations['belongsToMany'])&&count($relations['belongsToMany']))
    @foreach($relations['belongsToMany'] as $item1)
        @if($item1['weakness'])
            ${{$item1['related_table']}} = {{$item1['related_model_name']}}::all();
            $selected{{$item1['related_model_name']}} = [];
            @php
                array_push($weakness, $item1['related_table']);
                array_push($select_data, 'selected'.$item1['related_model_name']);
            @endphp
        @endif
    @endforeach
@endif
@php
    $enteredCompact=false;
@endphp
return view('backend.{{$tableName}}.create'@if(count($foreign)||count($weakness)),compact(
@foreach($foreign as $key=> $item1)@php
    $enteredCompact=true;
@endphp @if($key==0)"{{$item1['table']}}","selected{{$item1['modelName']}}"
@else ,"{{$item1['table']}}","selected{{$item1['modelName']}}"@endif @endforeach   @if(isset($weakness)&&count($weakness))
    @foreach($weakness as $key=> $item1)
        @if(!$enteredCompact)"{{$item1}}","{{$select_data[$key]}}"@else ,"{{$item1}}","{{$select_data[$key]}}" @endif
    @endforeach
@endif {{")"}} @endif
{{")"}};
}

/**
* Store a newly created {{$modelBaseName}} in storage.
*
* @param Create{{$modelBaseName}}Request $request
*
* @return Response | \Illuminate\View\View|Response
*/
public function store(Create{{$modelBaseName}} $request)
{
$obj=$this-> {{$modelVariableName}}Repository->create($request->only( ['{!! implode('\', \'', $fillable) !!}']));
@if(isset($relations['belongsToMany'])&&count($relations['belongsToMany']))
    @foreach($relations['belongsToMany'] as $item1)
        @if($item1['weakness'])
            if (isset($request->all()['{{$item1['related_table']}}'])) {
            foreach ($request->all()['{{$item1['related_table']}}'] as $item) {
            if (is_null($item))
            break;
            $obj1 = new {{$item1['middleTableModel']}}();
            $obj1->{{$modelVariableName}}_id = $obj->id;
            $obj1->{{$item1['related_class']}}_id = $item;
            $obj1->save();
            }
        }
        @endif
    @endforeach
@endif
return redirect()->route('admin.{{$modelVariableName}}.index')->withFlashSuccess(__('alerts.frontend.{{$modelVariableName}}.saved'));
}

/**
* Display the specified {{$modelBaseName}}.
*
* @param {{$modelBaseName}} ${{$modelVariableName}}
* @return \Illuminate\View\View|Response
* @internal param int $id
*
*/
public function show({{$modelBaseName}} ${{$modelVariableName}})
{
return view('backend.{{$tableName}}.show')->with('{{$modelVariableName}}', ${{$modelVariableName}});
}


/**
* Show the form for editing the specified {{$modelBaseName}}.
*
* @param {{$modelBaseName}} ${{$modelVariableName}}
* @return \Illuminate\View\View|Response
* @internal param int $id
*
*/
public function edit({{$modelBaseName}} ${{$modelVariableName}})
{
@if(count($foreign))
    @foreach($foreign as $item1)
        ${{$item1['table']}} = {{$item1['modelName']}}::all();
        $selected{{$item1['modelName']}} = {{$modelBaseName}}::first()->{{$item1['lowerModelName']}}_id;
    @endforeach
@endif
@php
    $weakness=[];
  $select_data=[];
@endphp
@if(isset($relations['belongsToMany'])&&count($relations['belongsToMany']))
    @foreach($relations['belongsToMany'] as $item1)
        @if($item1['weakness'])
            ${{$item1['related_table']}} = {{$item1['related_model_name']}}::all();
            $selected{{$item1['related_model_name']}} = [];
            $related_items = {{$item1['middleTableModel']}}::where('{{$modelVariableName}}_id', '=', ${{$modelVariableName}}->id)->get();
            foreach ($related_items as $related_item) {
            array_push($selected{{$item1['related_model_name']}}, $related_item->{{$item1['otherKey']}});
            }
            @php
                array_push($weakness, $item1['related_table']);
                array_push($select_data, 'selected'.$item1['related_model_name']);
            @endphp
        @endif
    @endforeach
@endif
@php
    $enteredCompact=false;
@endphp
return view('backend.{{$tableName}}.edit'@if(count($foreign)||count($weakness)),compact(
@foreach($foreign as $key=> $item1)@php
    $enteredCompact=true;
@endphp @if($key==0)"{{$item1['table']}}","selected{{$item1['modelName']}}"
@else ,"{{$item1['table']}}","selected{{$item1['modelName']}}"@endif @endforeach  @if(isset($weakness)&&count($weakness))
    @foreach($weakness as $key=> $item1)
        @if(!$enteredCompact)"{{$item1}}","{{$select_data[$key]}}"@else ,"{{$item1}}","{{$select_data[$key]}}" @endif
    @endforeach
@endif {{")"}}@endif
{{")"}}->with('{{$modelVariableName}}', ${{$modelVariableName}});
}


/**
* Update the specified {{$modelBaseName}} in storage.
*
* @param Update{{$modelBaseName}}Request $request
*
* @param {{$modelBaseName}} ${{$modelVariableName}}
* @return \Illuminate\View\View|Response
* @internal param int $id
*/
public function update(Update{{$modelBaseName}}  $request, {{$modelBaseName}} ${{$modelVariableName}})
{
$this->{{$modelVariableName}}Repository->update(${{$modelVariableName}}, $request->all());
@if(isset($relations['belongsToMany'])&&count($relations['belongsToMany']))
    @php
        $weakness=[];
      $select_data=[];
    @endphp
    @foreach($relations['belongsToMany'] as $item1)
        @if($item1['weakness'])
            if (isset($request->all()['{{$item1['related_table']}}'])) {
            $deleted = {{$item1['middleTableModel']}}::where('{{$modelVariableName}}_id', '=', ${{$modelVariableName}}->id)->get();
            foreach ($deleted as $item) {
            $item->delete();
            }

            foreach ($request->all()['{{$item1['related_table']}}'] as $item) {
            if (is_null($item))
            break;
            $relate_item = new {{$item1['middleTableModel']}}();
            $relate_item->{{$modelVariableName}}_id = ${{$modelVariableName}}->id;
            $relate_item->{{$item1['related_class']}}_id = $item;
            $relate_item->save();

            }
            }

            @php
                array_push($weakness, $item1['related_table']);
                array_push($select_data, 'selected'.$item1['related_model_name']);
            @endphp
        @endif
    @endforeach
@endif
return redirect()->route('admin.{{$modelVariableName}}.index')->withFlashSuccess(__('alerts.frontend.{{$modelVariableName}}.updated'));

}

/**
* Remove the specified {{$modelBaseName}} from storage.
*
* @param {{$modelBaseName}} ${{$modelVariableName}}
* @return \Illuminate\View\View|Response
* @internal param int $id
*
*/
public function destroy({{$modelBaseName}} ${{$modelVariableName}})
{
$this->{{$modelVariableName}}Repository->delete(${{$modelVariableName}});

return redirect()->back()->withFlashSuccess(__('alerts.frontend.{{$modelVariableName}}.deleted'));
}

}
